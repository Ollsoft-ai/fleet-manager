import requests
import time
import math
from typing import Dict, List
import json

# Constants
SCENARIO_ID = "8faa847f-2491-4523-ace9-6e96daaa2da5"  # Replace with your actual scenario ID
BASE_URL_RUNNER = "http://localhost:8090"
BASE_URL_BACKEND = "http://localhost:8080"
SIMULATION_SPEED = 0.2

def calculate_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def find_closest_available_vehicle(customer, vehicles):
    min_distance = float('inf')
    closest_vehicle = None
    
    for vehicle in vehicles:
        if vehicle['isAvailable']:
            distance = calculate_distance(
                customer['coordX'], 
                customer['coordY'],
                vehicle['coordX'], 
                vehicle['coordY']
            )
            if distance < min_distance:
                min_distance = distance
                closest_vehicle = vehicle
    
    return closest_vehicle

def initialize_scenario():
    # Initialize the scenario in the runner
    headers = {'Content-Type': 'application/json'}
    response = requests.post(
        f"{BASE_URL_RUNNER}/Scenarios/initialize_scenario",
        params={"db_scenario_id": SCENARIO_ID},
        headers=headers,
        json={}
    )
    if response.status_code != 200:
        raise Exception(f"Failed to initialize scenario: Status {response.status_code}")
    
    # Launch the scenario
    response = requests.post(
        f"{BASE_URL_RUNNER}/Runner/launch_scenario/{SCENARIO_ID}",
        params={"speed": SIMULATION_SPEED}
    )
    if response.status_code != 200:
        raise Exception("Failed to launch scenario")

def get_scenario_state():
    response = requests.get(f"{BASE_URL_RUNNER}/Scenarios/get_scenario/{SCENARIO_ID}")
    return response.json()

def update_vehicle_assignments(vehicle_updates):
    if not vehicle_updates:
        return
    
    payload = {"vehicles": vehicle_updates}
    response = requests.put(
        f"{BASE_URL_RUNNER}/Scenarios/update_scenario/{SCENARIO_ID}",
        json=payload
    )
    return response.json()

def main():
    print(f"Starting scenario {SCENARIO_ID}")
    initialize_scenario()
    
    while True:
        # Get current state
        scenario_state = get_scenario_state()
        
        if not scenario_state:
            print("Scenario completed or error occurred")
            break
        
        vehicles = scenario_state['vehicles']
        customers = scenario_state['customers']
        
        # Print current state with more detail
        print("\n=== Current State ===")
        print(f"Active Vehicles: {len([v for v in vehicles if not v['isAvailable']])}")
        print(f"Waiting Customers: {len([c for c in customers if c['awaitingService']])}")
        
        # Print vehicle positions with more details
        print("\n=== Vehicle Positions ===")
        for v in vehicles:
            status = "🚗 BUSY" if not v['isAvailable'] else "🚙 IDLE"
            customer_info = f", serving customer {v['customerId']}" if not v['isAvailable'] else ""
            print(f"Vehicle {v['id'][:8]}: ({v['coordX']:.2f}, {v['coordY']:.2f}) - {status}{customer_info}")
            print(f"  Speed: {v['vehicleSpeed']:.2f} m/s, Remaining Time: {v['remainingTravelTime']}s")
            print(f"  Distance Travelled: {v['distanceTravelled']:.2f}m, Trips: {v['numberOfTrips']}")

        # Print waiting customer positions
        print("\n=== Waiting Customers ===")
        for c in customers:
            if c['awaitingService']:
                print(f"Customer {c['id'][:8]}: Current ({c['coordX']:.2f}, {c['coordY']:.2f})")
                print(f"  Destination: ({c['destinationX']:.2f}, {c['destinationY']:.2f})")

        # Find waiting customers and available vehicles
        waiting_customers = [c for c in customers if c['awaitingService']]
        available_vehicles = [v for v in vehicles if v['isAvailable']]
        print(f"\nAvailable vehicles: {len(available_vehicles)}")
        
        vehicle_updates = []
        
        # Assign vehicles to customers
        for customer in waiting_customers:
            closest_vehicle = find_closest_available_vehicle(customer, vehicles)
            if closest_vehicle:
                vehicle_updates.append({
                    "id": closest_vehicle['id'],
                    "customerId": customer['id']
                })
                print(f"Assigning vehicle {closest_vehicle['id'][:8]} to customer {customer['id'][:8]}")
        
        # Update vehicle assignments
        if vehicle_updates:
            print(f"Sending {len(vehicle_updates)} vehicle updates...")
            update_result = update_vehicle_assignments(vehicle_updates)
            print(f"Update result: {update_result}")
        
        # Check if scenario is complete
        if not waiting_customers and all(v['isAvailable'] for v in vehicles):
            print("\nScenario completed!")
            break
        
        time.sleep(1)  # Wait before next update

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error occurred: {e}")