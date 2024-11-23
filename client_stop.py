import requests
import json

def main():
    # Base URL of your Flask application
    base_url = "http://localhost:80"  # Adjust if your port is different
    
    # Get scenarios
    print("Getting scenarios...")
    response = requests.get(f"{base_url}/scenarios")
    if response.status_code != 200:
        print(f"Failed to get scenarios: {response.status_code}")
        return
    
    scenarios = response.json()
    if not scenarios:
        print("No scenarios found")
        return
    
    # Get the first scenario's ID
    first_scenario = scenarios[0]
    scenario_id = first_scenario['id']
    print(f"Found scenario with ID: {scenario_id}")
    
    # Stop the scenario
    print(f"Stopping scenario {scenario_id}...")
    response = requests.post(f"{base_url}/stop/{scenario_id}")
    if response.status_code != 200:
        print(f"Failed to stop scenario: {response.status_code} {response.text}")
        return
    
    result = response.json()
    print(f"Success! {result['message']}")

if __name__ == "__main__":
    main() 