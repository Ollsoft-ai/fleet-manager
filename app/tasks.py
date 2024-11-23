import requests
import time
from app.celery_app import celery
import redis
import json
from datetime import datetime

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

def calculate_distance(point1_x, point1_y, point2_x, point2_y):
    """Calculate Euclidean distance between two points."""
    return ((point1_x - point2_x) ** 2 + (point1_y - point2_y) ** 2) ** 0.5

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

def update_scenario_metadata(scenario_id, scenario_state):
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
    total_distance = sum(v["distanceTravelled"] for v in scenario_state["vehicles"])
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
            'total_distance_without_customer': 0,  # Need additional tracking
            'total_distance_with_customer': total_distance,  # Assuming all distance is with customer for now
            'average_customer_wait_time': 0,  # Need additional tracking
            'realtime_kpis': {
                'completion_rate': completion_rate,
                'fuel_saved': 0,  # Need optimal route calculation
                'total_travel_time': total_active_time,
                'total_travel_distance': total_distance,
                'average_number_of_trips_per_vehicle': avg_trips_per_vehicle,
                'number_of_waiting_customers': waiting_customers,
                'number_of_available_vehicles': available_vehicles,
                'number_of_taken_vehicles': taken_vehicles,
                'average_customer_trip_distance': avg_customer_trip_distance,
                'average_vehicle_speed': avg_vehicle_speed
            }
        }
    })
    print("redis metadata updated")
    # Store updated metadata in Redis
    redis_client.set(f"scenario_metadata:{scenario_id}", json.dumps(metadata))

@celery.task(bind=True)
def run_scenario_controller(self, scenario_id):
    """Background task that runs the scenario controller algorithm with precomputed assignments"""
    # Initialize metadata
    metadata = {
        'start_time': datetime.now().isoformat(),
        'vehicle_assignments': {},
        'realtime_positions': {}
    }
    redis_client.set(f"scenario_metadata:{scenario_id}", json.dumps(metadata))
    
    # Track current vehicle-customer assignments
    current_assignments = {}  # vehicle_id -> customer_id

    while True:
        current_scenario_state = get_scenario_state(scenario_id)
        
        # Update metadata every loop iteration
        update_scenario_metadata(scenario_id, current_scenario_state)
        
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
            update_scenario_metadata(scenario_id, current_scenario_state)
            print("No more customers waiting, ending simulation")
            break
            
        # Process assignments for free vehicles
        for vehicle, customer in assignments:
            update_vehicle_assignment(scenario_id, vehicle["id"], customer["id"])
            current_assignments[vehicle["id"]] = customer["id"]
            print(f"Assigned customer {customer['id']} to vehicle {vehicle['id']}")
            
        time.sleep(0.005)  # Short sleep to prevent overwhelming the system