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
SIMULATION_SPEED = 0.0005

# Add this to store active scenario tasks
active_scenarios = {}

# Add Redis connection
redis_client = Redis(host='redis', port=6379, db=0)

@main.route('/')
def index():
    # redirect to map
    return redirect(url_for('main.map'))

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

@main.route("/scenario_template/<scenario_id>", methods=['GET'])
def scenario_template(scenario_id):
    headers = {'Content-Type': 'application/json'}
    response = requests.get(
        f"{BASE_URL_BACKEND}/scenarios/{scenario_id}",
        headers=headers
    )
    if response.status_code != 200:
        return {"error": f"Failed to get scenario template: Status {response.status_code}"}, response.status_code
    return response.json()

@main.route('/run/<scenario_id>', methods=['POST']) # second you run the scenario
def run(scenario_id):
    # Get algorithm type from request parameters, default to "optimized"
    algorithm = request.args.get('algorithm', 'optimized')
    
    if algorithm not in ['optimized', 'naive', "cpp_optimized"]:
        return {"error": "Invalid algorithm type. Must be 'optimized' or 'naive' or 'cpp_optimized'"}, 400

    # get scenario from db
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

    # Start the controller task with the specified algorithm
    task = run_scenario_controller.delay(scenario_id, algorithm=algorithm)
    active_scenarios[scenario_id] = task.id
    
    return {"message": "Simulation started", "task_id": task.id, "algorithm": algorithm}, 200

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

    # Get metadata from Redis and decode it properly
    metadata = redis_client.get(f"scenario_metadata:{scenario_id}")
    if metadata:
        # Decode bytes to string and parse JSON
        current_scenario_state['metadata'] = json.loads(metadata.decode('utf-8'))
    else:
        current_scenario_state['metadata'] = None

    return current_scenario_state

    
@main.route('/map')
def map():
    return render_template('map.html')


@main.route('/analytics')
def analytics():
    simulation_id = request.args.get('simId')
    return render_template('analytics.html', simulation_id=simulation_id)


@main.route('/environment')
def environment():
    return render_template('environment.html')

@main.route('/vehicles')
def vehicles(): 
    return render_template('vehicles.html')
#@main.app_context_processor
#def inject_conf_var():
#    return dict(
#        current_app.config['LANGUAGES'],
#    )
