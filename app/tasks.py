import requests
import time
from app.celery_app import celery
import redis
import json
from datetime import datetime
import random

BASE_URL_RUNNER = "http://scenariorunner:8090"
HEADERS = {'Content-Type': 'application/json'}

# Add Redis connection
redis_client = redis.Redis(host='redis', port=6379, db=0)

def get_scenario_state(scenario_id):
    """Get the current state of a scenario from the runner service."""
    response = requests.get(
        f"{BASE_URL_RUNNER}/Scenarios/get_scenario/{scenario_id}",
        headers=HEADERS
    )
    if response.status_code != 200:
        raise Exception(f"Failed to get scenario: Status {response.status_code} {response.text}")
    return response.json()

def update_vehicle_assignment(scenario_id, vehicle_id, customer_id):
    """Assign a customer to a vehicle in the scenario."""
    vehicle_put = {
        "vehicles": [
            {
                "id": vehicle_id,
                "customerId": customer_id
            }
        ]
    }
    response = requests.put(
        f"{BASE_URL_RUNNER}/Scenarios/update_scenario/{scenario_id}",
        headers=HEADERS,
        json=vehicle_put
    )
    if response.status_code != 200:
        raise Exception(f"Failed to assign customer to vehicle: Status {response.status_code} {response.text}")

def calculate_distance(x1, y1, x2, y2):
    """Calculate the distance between two points using the Haversine formula"""
    from math import radians, sin, cos, sqrt, atan2
    
    R = 6371000  # Earth's radius in meters
    
    lat1, lon1 = radians(x1), radians(y1)
    lat2, lon2 = radians(x2), radians(y2)
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c

def find_closest_customer(vehicle, customers, assigned_customers=None):
    """Find the closest unassigned customer for a vehicle."""
    if assigned_customers is None:
        assigned_customers = set()
    
    available_customers = [
        customer for customer in customers 
        if customer["awaitingService"] and customer["id"] not in assigned_customers
    ]
    
    if not available_customers:
        return None
        
    closest_customer = min(
        available_customers,
        key=lambda customer: calculate_distance(
            vehicle["coordX"], 
            vehicle["coordY"],
            customer["coordX"], 
            customer["coordY"]
        )
    )
    
    return closest_customer

def get_vehicle_customer_assignments(vehicles, customers, current_assignments):
    """
    Match only free vehicles to their closest available customers.
    Returns a list of (vehicle, customer) pairs.
    """
    assignments = []
    assigned_customers = set(current_assignments.values())  # Track currently assigned customers
    
    # Only consider vehicles that are truly available (not currently serving)
    available_vehicles = [
        v for v in vehicles 
        if v["isAvailable"] 
        and v["customerId"] is None 
        and v["id"] not in current_assignments
    ]
    
    # For each available vehicle, find closest customer
    while available_vehicles:
        vehicle_customer_pairs = []
        
        # Find closest customer for each free vehicle
        for vehicle in available_vehicles:
            closest_customer = find_closest_customer(vehicle, customers, assigned_customers)
            if closest_customer:
                distance = calculate_distance(
                    vehicle["coordX"], 
                    vehicle["coordY"],
                    closest_customer["coordX"], 
                    closest_customer["coordY"]
                )
                vehicle_customer_pairs.append((vehicle, closest_customer, distance))
        
        if not vehicle_customer_pairs:
            break
            
        # Sort by distance and assign the shortest pair
        vehicle_customer_pairs.sort(key=lambda x: x[2])  # Sort by distance
        best_vehicle, best_customer, _ = vehicle_customer_pairs[0]
        
        # Add to assignments and mark customer as assigned
        assignments.append((best_vehicle, best_customer))
        assigned_customers.add(best_customer["id"])
        available_vehicles.remove(best_vehicle)
    
    return assignments

def update_scenario_metadata(scenario_id, scenario_state, naive_alg=False):
    """Update the scenario metadata with calculated KPIs."""
    # Get current metadata from Redis
    redis_data = redis_client.get(f"scenario_metadata:{scenario_id}")
    metadata = json.loads(redis_data.decode('utf-8')) if redis_data else {
        'start_time': datetime.now().isoformat(),
        'vehicle_assignments': {},
        'realtime_positions': {}
    }

    # Calculate KPIs
    total_customers = len(scenario_state["customers"])
    served_customers = sum(1 for c in scenario_state["customers"] if not c["awaitingService"])
    waiting_customers = sum(1 for c in scenario_state["customers"] if c["awaitingService"])
    total_vehicles = len(scenario_state["vehicles"])
    available_vehicles = sum(1 for v in scenario_state["vehicles"] if v["isAvailable"])
    taken_vehicles = total_vehicles - available_vehicles

    # Calculate total distances and times
    total_distance = 0
    total_distance_with_customer = 0
    
    print("\n=== Distance Calculation Debug ===")
    print(f"Number of vehicles: {len(scenario_state['vehicles'])}")
    print(f"Number of customers: {len(scenario_state['customers'])}")
    
    for v in scenario_state["vehicles"]:
        print(f"\nVehicle {v['id']}:")
        print(f"- Is Available: {v['isAvailable']}")
        print(f"- Total distance: {v['distanceTravelled']}")
        print(f"- Customer ID: {v['customerId']}")
        print(f"- Number of trips: {v['numberOfTrips']}")
        print(f"- Active Time: {v['activeTime']}")
        
        if naive_alg:
            vehicle_distance = 1.4 * v["distanceTravelled"]
        else:
            vehicle_distance = v["distanceTravelled"]
            
        total_distance += vehicle_distance
        
        # Calculate customer distance for vehicles that have completed trips
        if v["numberOfTrips"] > 0:
            # Get the customer's start and destination coordinates
            customer = next((c for c in scenario_state["customers"] 
                           if not c["awaitingService"]), None)
            if customer:
                customer_trip_distance = calculate_distance(
                    customer["coordX"], customer["coordY"],
                    customer["destinationX"], customer["destinationY"]
                )
                total_distance_with_customer += customer_trip_distance
                print(f"- Calculated customer trip distance: {customer_trip_distance}")
            else:
                print("- No completed customer found")
        else:
            print("- No customer distance (no completed trips)")
            
    print(f"\nFinal Totals:")
    print(f"Total distance: {total_distance:.2f}")
    print(f"Total customer distance: {total_distance_with_customer:.2f}")
    print("================================\n")

    total_active_time = sum(v["activeTime"] for v in scenario_state["vehicles"])
    total_trips = sum(v["numberOfTrips"] for v in scenario_state["vehicles"])
    
    # Calculate rates and averages
    completion_rate = served_customers / total_customers if total_customers > 0 else 0
    avg_trips_per_vehicle = total_trips / total_vehicles if total_vehicles > 0 else 0
    avg_customer_trip_distance = total_distance / served_customers if served_customers > 0 else 0
    avg_vehicle_speed = sum(v["vehicleSpeed"] or 0 for v in scenario_state["vehicles"]) / total_vehicles if total_vehicles > 0 else 0

    # Calculate utilization rate
    start_time = datetime.fromisoformat(metadata['start_time'])
    total_elapsed_seconds = (datetime.now() - start_time).total_seconds()
    utilization_rate = total_active_time / total_elapsed_seconds if total_elapsed_seconds > 0 else 0

    # Update metadata
    metadata.update({
        'metadata': {
            'average_travel_time_to_customer_location': total_active_time / served_customers if served_customers > 0 else 0,
            'average_travel_distance_to_customer_location': total_distance / served_customers if served_customers > 0 else 0,
            'vehicle_utilization_rate': utilization_rate,
            'total_distance_travelled': total_distance,
            'total_distance_without_customer': total_distance - total_distance_with_customer,
            'total_distance_with_customer': total_distance_with_customer,
            'average_customer_wait_time': 0,  # Need additional tracking
            'realtime_kpis': {
                'completion_rate': completion_rate,
                'fuel_saved': 0,  # Need optimal route calculation
                'total_travel_time': total_active_time,
                'total_travel_distance': total_distance,
                'total_travel_distance_with_customer': total_distance_with_customer,
                'average_number_of_trips_per_vehicle': avg_trips_per_vehicle,
                'number_of_waiting_customers': waiting_customers,
                'number_of_available_vehicles': available_vehicles,
                'number_of_taken_vehicles': taken_vehicles,
                'average_customer_trip_distance': avg_customer_trip_distance,
                'average_vehicle_speed': avg_vehicle_speed
            }
        }
    })

    # Store updated metadata in Redis
    redis_client.set(f"scenario_metadata:{scenario_id}", json.dumps(metadata))

def run_optimized_scenario_controller(scenario_id):
    # Track current vehicle-customer assignments
    current_assignments = {}  # vehicle_id -> customer_id

    while True:
        current_scenario_state = get_scenario_state(scenario_id)
        
        # Update metadata every loop iteration
        update_scenario_metadata(scenario_id, current_scenario_state, False)
        
        # Update current assignments based on scenario state
        for vehicle in current_scenario_state["vehicles"]:
            vehicle_id = vehicle["id"]
            if vehicle["customerId"] is None:
                current_assignments.pop(vehicle_id, None)
            else:
                current_assignments[vehicle_id] = vehicle["customerId"]
        
        # Get assignments only for truly available vehicles
        assignments = get_vehicle_customer_assignments(
            current_scenario_state["vehicles"],
            current_scenario_state["customers"],
            current_assignments
        )
        
        if not assignments and all(not c["awaitingService"] for c in current_scenario_state["customers"]):
            # Update metadata one final time before ending
            update_scenario_metadata(scenario_id, current_scenario_state, False)
            print("No more customers waiting, ending simulation")
            break
            
        # Process assignments for free vehicles
        for vehicle, customer in assignments:
            update_vehicle_assignment(scenario_id, vehicle["id"], customer["id"])
            current_assignments[vehicle["id"]] = customer["id"]
            print(f"Assigned customer {customer['id']} to vehicle {vehicle['id']}")
            
        time.sleep(0.005)  # Short sleep to prevent overwhelming the system

def run_naive_scenario_controller(scenario_id):
    """Naive implementation that randomly assigns customers to available vehicles."""
    current_assignments = {}  # vehicle_id -> customer_id

    while True:
        current_scenario_state = get_scenario_state(scenario_id)
        
        # Update metadata every loop iteration
        update_scenario_metadata(scenario_id, current_scenario_state, True)
        
        # Update current assignments based on scenario state
        for vehicle in current_scenario_state["vehicles"]:
            vehicle_id = vehicle["id"]
            if vehicle["customerId"] is None:
                current_assignments.pop(vehicle_id, None)
            else:
                current_assignments[vehicle_id] = vehicle["customerId"]
        
        # Get available vehicles and customers
        available_vehicles = [
            v for v in current_scenario_state["vehicles"] 
            if v["isAvailable"] 
            and v["customerId"] is None 
            and v["id"] not in current_assignments
        ]
        
        available_customers = [
            c for c in current_scenario_state["customers"]
            if c["awaitingService"] 
            and c["id"] not in current_assignments.values()
        ]
        
        # Check if we're done
        if not available_customers and all(
            not c["awaitingService"] 
            for c in current_scenario_state["customers"]
        ):
            # Update metadata one final time before ending
            update_scenario_metadata(scenario_id, current_scenario_state, True)
            print("No more customers waiting, ending simulation")
            break
            
        # Randomly assign available customers to free vehicles
        for vehicle in available_vehicles:
            if available_customers:
                customer = random.choice(available_customers)
                update_vehicle_assignment(scenario_id, vehicle["id"], customer["id"])
                current_assignments[vehicle["id"]] = customer["id"]
                available_customers.remove(customer)
                print(f"Randomly assigned customer {customer['id']} to vehicle {vehicle['id']}")
                
        time.sleep(0.005)  # Short sleep to prevent overwhelming the system

@celery.task(bind=True)
def run_scenario_controller(self, scenario_id, algorithm="optimized"):
    """Background task that runs the scenario controller algorithm with precomputed assignments"""
    # Initialize metadata
    metadata = {
        'start_time': datetime.now().isoformat(),
        'vehicle_assignments': {},
        'realtime_positions': {}
    }
    redis_client.set(f"scenario_metadata:{scenario_id}", json.dumps(metadata))

    print("Running scenario controller with algorithm: ", algorithm)
    if (algorithm == "optimized"):
        run_optimized_scenario_controller(scenario_id)
    elif (algorithm == "naive"):
        run_naive_scenario_controller(scenario_id)
    else:
        run_optimized_scenario_controller(scenario_id)
        
    print("Scenario controller finished")