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

def get_vehicle_customer_assignments(vehicles, customers):
    """
    Match vehicles to their closest available customers.
    Returns a list of (vehicle, customer) pairs.
    """
    assignments = []
    assigned_customers = set()
    
    # Sort vehicles by their availability
    available_vehicles = [v for v in vehicles if v["isAvailable"]]
    
    # For each customer, find which vehicle can reach it fastest
    while available_vehicles:
        vehicle_customer_pairs = []
        
        # Find closest customer for each vehicle
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

def update_scenario_metadata(scenario_id, vehicle_id):
    """Update the scenario metadata in Redis."""
    vehicle_metadata = {}
    metadata = json.loads(redis_client.get(f"scenario_metadata:{scenario_id}") or '{}')
    metadata['vehicle_assignments'][vehicle_id] = vehicle_metadata
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

    while True:
        current_scenario_state = get_scenario_state(scenario_id)
        
        # Get all assignments for available vehicles
        assignments = get_vehicle_customer_assignments(
            current_scenario_state["vehicles"],
            current_scenario_state["customers"]
        )
        
        if not assignments:
            print("No more assignments possible, ending simulation")
            break
            
        # Process all assignments
        for vehicle, customer in assignments:
            update_vehicle_assignment(scenario_id, vehicle["id"], customer["id"])
            update_scenario_metadata(scenario_id, vehicle["id"])
            print(f"Assigned customer {customer['id']} to vehicle {vehicle['id']}")
            
        time.sleep(0.005)