import requests
import time
from app.celery_app import celery
import redis
import json
from datetime import datetime

BASE_URL_RUNNER = "http://scenariorunner:8090"

# Add Redis connection
redis_client = redis.Redis(host='redis', port=6379, db=0)

@celery.task(bind=True)
def run_scenario_controller(self, scenario_id):
    """Background task that runs the scenario controller algorithm with precomputed assignments"""
    # Get initial scenario state
    headers = {'Content-Type': 'application/json'}
    
    # Initialize metadata for this scenario run
    metadata = {
        'start_time': datetime.now().isoformat(),
        'vehicle_assignments': {},
        'realtime_positions': {}
    }
    redis_client.set(f"scenario_metadata:{scenario_id}", json.dumps(metadata))

    while True:
        # get current scenario state
        response = requests.get(
            f"{BASE_URL_RUNNER}/Scenarios/get_scenario/{scenario_id}",
            headers=headers
        )
        if response.status_code != 200:
            raise Exception(f"Failed to get scenario: Status {response.status_code} {response.text}")
        
        current_scenario_state = response.json()

        # select what vehicle goes to what customer
        vehicle_to_run = current_scenario_state["vehicles"][0]
        customer_to_run = None
        for customer in current_scenario_state["customers"]:
            if customer["awaitingService"]:
                customer_to_run = customer
                break

        if customer_to_run is None:
            print("No customer to run, ending simulation")
            break

        # assign customer to vehicle and update scenario
        if vehicle_to_run["isAvailable"] and customer_to_run:
            vehicle_put = {
                "vehicles": [
                    {
                        "id": vehicle_to_run["id"],
                        "customerId": customer_to_run["id"]
                    }
                ]
            }
            # assign customer to vehicle
            response = requests.put(
                f"{BASE_URL_RUNNER}/Scenarios/update_scenario/{scenario_id}",
                headers=headers,
                json=vehicle_put
            )
            if response.status_code != 200:
                raise Exception(f"Failed to assign customer to vehicle: Status {response.status_code} {response.text}")

            # get current scenario state
            response = requests.get(
                f"{BASE_URL_RUNNER}/Scenarios/get_scenario/{scenario_id}",
                headers=headers
            )
            if response.status_code != 200:
                raise Exception(f"Failed to get scenario: Status {response.status_code} {response.text}")
            
            current_scenario_state = response.json()
            vehicle_to_run = current_scenario_state["vehicles"][0]
            customer_to_run = current_scenario_state["customers"][0]

            # Store initial position and time for interpolation
            vehicle_metadata = {
                'start_time': datetime.now().isoformat(),
                'start_position': {
                    'x': vehicle_to_run['coordX'],
                    'y': vehicle_to_run['coordY']
                },
                'target_position': {
                    'x': customer_to_run['coordX'],
                    'y': customer_to_run['coordY']
                },
                'initial_travel_time': vehicle_to_run['remainingTravelTime']
            }
            
            # Update metadata in Redis
            metadata = json.loads(redis_client.get(f"scenario_metadata:{scenario_id}") or '{}')
            metadata['vehicle_assignments'][vehicle_to_run['id']] = vehicle_metadata
            redis_client.set(f"scenario_metadata:{scenario_id}", json.dumps(metadata))
            print(f"Assigned customer {customer_to_run['id']} to vehicle {vehicle_to_run['id']}")

        # print the first car
        print(f"vehicle: remaining time: {vehicle_to_run['remainingTravelTime']}, x and y coord: {vehicle_to_run['coordX']}, {vehicle_to_run['coordY']}")
        print(f"customer: awaiting service: {customer_to_run['awaitingService']}, x and y coord: {customer_to_run['coordX']}, {customer_to_run['coordY']}")
        print("--------------------------------")
        time.sleep(0.5)