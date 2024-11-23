import requests
from flask import render_template, request, redirect, url_for, session, current_app
from . import main

BASE_URL_RUNNER = "http://scenariorunner:8090"
BASE_URL_BACKEND = "http://backend:8080"
SIMULATION_SPEED = 0.2

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
        return {"error": f"Failed to initialize scenario: Status {response.status_code}"}, response.status_code

    # start simulation
    response = requests.post(
        f"{BASE_URL_RUNNER}/Runner/launch_scenario/{scenario_id}",
        headers=headers,
        json={"speed": SIMULATION_SPEED}
    )
    if response.status_code != 200:
        return {"error": f"Failed to start simulation: Status {response.status_code}"}, response.status_code
    
    return {"message": "Simulation started"}, 200

@main.route('/stop/<scenario_id>', methods=['POST'])
def stop(scenario_id):
    """Currently there is no "stop running option" for a running scenario. A running scenario is marked complete only when all customers have awaitingService=false. To prematurely end a scenario either:
    Edit the Db directly to set the awaitingService property of all customers to "false"."""
    return "Simulation stopped"

@main.route('/scenario/<scenario_id>', methods=['GET']) # you can get the current state of the scenario by this
def scenario(scenario_id):
    headers = {'Content-Type': 'application/json'}
    # get current scenario state
    response = requests.get(
        f"{BASE_URL_RUNNER}/Scenarios/get_scenario/{scenario_id}",
        headers=headers
    )
    if response.status_code != 200:
        return {"error": f"Failed to get scenario: Status {response.status_code}"}, response.status_code
    
    current_scenario_state = response.json()

    return current_scenario_state

#@main.app_context_processor
#def inject_conf_var():
#    return dict(
#        current_app.config['LANGUAGES'],
#    )
