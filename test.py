import requests
import json
import time
# Constants
SCENARIO_ID = "8dc13b21-bc5f-46b1-a231-960d111314ad"  # Replace with your actual scenario ID
BASE_URL_RUNNER = "http://localhost:8090"
BASE_URL_BACKEND = "http://localhost:8080"
SIMULATION_SPEED = 0.2

#get scneario from db
headers = {'Content-Type': 'application/json'}
response = requests.get(
    f"{BASE_URL_BACKEND}/scenarios/{SCENARIO_ID}",
    headers=headers
)
if response.status_code != 200:
    raise Exception(f"Scenario {SCENARIO_ID} doesnt exist in database {response.text}")

scenario = response.json()

# put scenario in runner
response = requests.post(
    f"{BASE_URL_RUNNER}/Scenarios/initialize_scenario",
    headers=headers,
    json=scenario
)
if response.status_code != 200:
    raise Exception(f"Failed to initialize scenario: Status {response.status_code} {response.text}")

# start simulation
response = requests.post(
    f"{BASE_URL_RUNNER}/Runner/launch_scenario/{SCENARIO_ID}",
    headers=headers,
    json={"speed": SIMULATION_SPEED}
)
if response.status_code != 200:
    raise Exception(f"Failed to start simulation: Status {response.status_code} {response.text}")

print("Simulation started")

while True:
    # get current scenario state
    response = requests.get(
        f"{BASE_URL_RUNNER}/Scenarios/get_scenario/{SCENARIO_ID}",
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
        print("No customer to run")
        break

    # assign customer to vehicle and update scenario
    if vehicle_to_run["isAvailable"]:
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
            f"{BASE_URL_RUNNER}/Scenarios/update_scenario/{SCENARIO_ID}",
            headers=headers,
            json=vehicle_put
        )
        if response.status_code != 200:
            raise Exception(f"Failed to assign customer to vehicle: Status {response.status_code} {response.text}")
        print(f"Assigned customer {customer_to_run['id']} to vehicle {vehicle_to_run['id']}")

    # print the first car
    print(current_scenario_state["vehicles"][0])
    time.sleep(0.5)
