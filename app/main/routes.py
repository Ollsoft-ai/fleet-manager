import requests
from flask import render_template, request, redirect, url_for, session, current_app
from . import main
from app.tasks import run_scenario_controller
from app.celery_app import celery
import json
from datetime import datetime
from redis import Redis

BASE_URL_RUNNER = "http://scenariorunner:8090"
BASE_URL_BACKEND = "http://backend:8080"
SIMULATION_SPEED = 0.05

# Add this to store active scenario tasks
active_scenarios = {}

# Add Redis connection
redis_client = Redis(host='redis', port=6379, db=0)

@main.route('/')
def index():
    return render_template('index.html')

@main.route("/scenarios", methods=['GET']) # first you get scenario id from this
def scenarios():
    headers = {'Content-Type': 'application/json'}
    response = requests.get(
        f"{BASE_URL_BACKEND}/scenarios",
        headers=headers
    )
    if response.status_code != 200:
        return {"error": f"Failed to get scenarios: Status {response.status_code}"}, response.status_code
    return response.json()

@main.route('/run/<scenario_id>', methods=['POST']) # second you run the scenario
def run(scenario_id):
    #get scneario from db
    headers = {'Content-Type': 'application/json'}
    response = requests.get(
        f"{BASE_URL_BACKEND}/scenarios/{scenario_id}",
        headers=headers
    )
    if response.status_code != 200:
        return {"error": f"Scenario {scenario_id} doesn't exist in database"}, response.status_code

    scenario = response.json()

    # put scenario in runner
    response = requests.post(
        f"{BASE_URL_RUNNER}/Scenarios/initialize_scenario",
        headers=headers,
        json=scenario
    )
    if response.status_code != 200:
        return {"error": f"Failed to initialize scenario: Status {response.status_code} {response.text}"}, response.status_code

    # start simulation
    response = requests.post(
        f"{BASE_URL_RUNNER}/Runner/launch_scenario/{scenario_id}",
        headers=headers,
        params={"speed": SIMULATION_SPEED}
    )
    if response.status_code != 200:
        return {"error": f"Failed to start simulation: Status {response.status_code} {response.text}"}, response.status_code

    # Start the controller task
    task = run_scenario_controller.delay(scenario_id)
    active_scenarios[scenario_id] = task.id
    
    return {"message": "Simulation started", "task_id": task.id}, 200

@main.route('/stop/<scenario_id>', methods=['POST'])
def stop(scenario_id):
    if scenario_id in active_scenarios:
        # Revoke the Celery task
        celery.control.revoke(active_scenarios[scenario_id], terminate=True)
        # Clean up Redis metadata
        redis_client.delete(f"scenario_metadata:{scenario_id}")
        del active_scenarios[scenario_id]
        return {"message": "Simulation stopped"}, 200
    return {"error": "No active simulation found"}, 404

@main.route('/scenario/<scenario_id>', methods=['GET']) # you can get the current state of the scenario by this
def scenario(scenario_id):
    headers = {'Content-Type': 'application/json'}
    # get current scenario state
    response = requests.get(
        f"{BASE_URL_RUNNER}/Scenarios/get_scenario/{scenario_id}",
        headers=headers
    )
    if response.status_code != 200:
        return {"error": f"Failed to get scenario: Status {response.status_code} {response.text}"}, response.status_code
    
    current_scenario_state = response.json()

    # Get metadata from Redis
    metadata = redis_client.get(f"scenario_metadata:{scenario_id}")
    if metadata:
        metadata = json.loads(metadata)
        # Calculate interpolated positions for vehicles
        current_time = datetime.now()
        for vehicle_id, vehicle_data in metadata['vehicle_assignments'].items():
            start_time = datetime.fromisoformat(vehicle_data['start_time'])
            time_diff = (current_time - start_time).total_seconds()
            initial_time = vehicle_data['initial_travel_time']
            
            if initial_time > 0:
                progress = min(1.0, time_diff / initial_time)
                
                # Linear interpolation of position
                start_pos = vehicle_data['start_position']
                target_pos = vehicle_data['target_position']
                
                interpolated_x = start_pos['x'] + (target_pos['x'] - start_pos['x']) * progress
                interpolated_y = start_pos['y'] + (target_pos['y'] - start_pos['y']) * progress
                
                metadata['realtime_positions'][vehicle_id] = {
                    'x': interpolated_x,
                    'y': interpolated_y,
                    'progress': progress
                }
        
        current_scenario_state['metadata'] = metadata

    return current_scenario_state

    
@main.route('/map')
def map():
    return render_template('map.html')

#@main.app_context_processor
#def inject_conf_var():
#    return dict(
#        current_app.config['LANGUAGES'],
#    )
