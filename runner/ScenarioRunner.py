import random
import threading
import requests
import time
import uuid
from datetime import datetime

from flask import request, jsonify
from flask_restx import Resource, Namespace, reqparse

from ApiModels import scenario_model
from ApiModels import update_scenario_model, api, app
from Classes import Scenario
from Classes import VehicleData, ScenarioMetadata
from DbConfig import session
from Utils import calculate_remaining_travel_time, calculate_distance

scenariosCrudApi = Namespace('Scenarios', description='Scenario operations')
scenarioRunnerApi = Namespace('Runner', description='Scenario runner operations')

api.add_namespace(scenariosCrudApi)
api.add_namespace(scenarioRunnerApi)

# In-memory storage for scenarios
scenarios = {}

parser = reqparse.RequestParser()
parser.add_argument('db_scenario_id', type=str, required=False,
                    help='The ID of the scenario (optional if request body is provided)', location='args')

# Define API Endpoints
@scenariosCrudApi.route('/initialize_scenario')
class InitializeScenario(Resource):
    @api.expect(scenario_model, parser)
    def post(self):
        db_scenario_id = request.args.get('db_scenario_id')
        data = request.get_json()
        if not data and not db_scenario_id:
            return {"error": "No scenario data provided"}, 400
        if not data:
            data = requests.get("http://backend:8080/scenarios/" + db_scenario_id).json()
        scenario_id = data["id"]

        if not is_valid_uuid(scenario_id):
            return {"error": f"Scenario ID '{scenario_id}' is not a valid UUID"}, 400
        # Check if scenario already exists and delete it if true
        if scenario_id in scenarios:
            if scenarios[scenario_id].status == 'RUNNING':
                return {"error": f"Scenario with ID {scenario_id} is already running"}, 400
            del scenarios[scenario_id]

        # Check for duplicate vehicle and customer IDs across scenarios
        existing_vehicle_ids = {vehicle.id for scenario in scenarios.values() for vehicle in scenario.vehicles}
        existing_customer_ids = {customer.id for scenario in scenarios.values() for customer in scenario.customers}

        # Validate the scenario ID, vehicle IDs, and customer IDs
        for vehicle_data in data.get("vehicles", []):
            vehicle_id = vehicle_data["id"]
            if not is_valid_uuid(vehicle_id):
                return {"error": f"Vehicle ID '{vehicle_id}' is not a valid UUID"}, 400
            if vehicle_id in existing_vehicle_ids:
                return {"error": f"Vehicle with ID {vehicle_id} is already associated with another scenario"}, 400

        # Validate vehicles
        for vehicle_data in data.get("vehicles", []):
            if vehicle_data["id"] in existing_vehicle_ids:
                return {"message": f"Vehicle with ID {vehicle_data['id']} is already associated with another scenario"}, 400

        # Validate customers
        for customer_data in data.get("customers", []):
            if customer_data["id"] in existing_customer_ids:
                return {"message": f"Customer with ID {customer_data['id']} is already associated with another scenario"}, 400

        # Create Scenario object
        scenario = Scenario(
            id=scenario_id,
            startTime=data.get("startTime"),
            endTime=data.get("endTime"),
            status=data.get("status")
        )

        # Add vehicles to the scenario
        for vehicle_data in data.get("vehicles", []):
            scenario.add_vehicle(vehicle_data)
            scenario.vehicles[-1].distanceTravelled = 0
            scenario.vehicles[-1].activeTime = 0
            scenario.vehicles[-1].numberOfTrips = 0
            scenario.vehicles[-1].remainingTravelTime = 0

        # Add customers to the scenario
        for customer_data in data.get("customers", []):
            scenario.add_customer(customer_data)

        # Store scenario in memory
        scenarios[scenario_id] = scenario

        return jsonify({"message": "Scenario initialised successfully", "scenario": scenario.to_dict()})


@scenariosCrudApi.route('/get_scenario/<string:scenario_id>')
class GetScenario(Resource):
    def get(self, scenario_id):
        scenario = scenarios.get(scenario_id)
        if scenario:
            return jsonify(scenario.to_dict())
        else:
            return {"message": "Scenario not found"}, 404


@scenariosCrudApi.route('/update_scenario/<string:scenario_id>')
class UpdateScenario(Resource):
    @api.expect(update_scenario_model, validate=True)
    def put(self, scenario_id):
        # Find the scenario by ID
        scenario = scenarios.get(scenario_id)
        if not scenario:
            return {"message": "Scenario not found"}, 404

        if scenario.status == 'COMPLETED':
            return {"message": "Scenario is already completed"}, 400

        # Get the JSON data for the update
        data = request.get_json()
        updated_vehicles = []
        non_updated_vehicles = []

        # Update vehicles
        for updated_vehicle in data.get("vehicles", []):
            vehicle_id = updated_vehicle.get("id")
            vehicle_travel_speed = random.uniform(8.33, 13.89)  # Random speed between 30 and 50 km/h
            vehicle = next((v for v in scenario.vehicles if v.id == vehicle_id), None)
            if not vehicle:
                print(f"Vehicle with ID {vehicle_id} not found in scenario {scenario_id}")
                non_updated_vehicles.append(vehicle_id)
                continue

            # Validate and apply updates
            if vehicle.isAvailable is False:
                print(f"Cannot update vehicle {vehicle_id}, vehicle is not available")
                non_updated_vehicles.append(vehicle_id)
                continue

            if "customerId" in updated_vehicle:
                # Enforce `isAvailable` and `awaitingService` conditions
                if vehicle.customerId != "" and vehicle.customerId is not None:
                    print (f"Cannot assign customer to vehicle {vehicle_id}, vehicle is already commissioned")
                    non_updated_vehicles.append(vehicle_id)
                    continue
                customer = next((c for c in scenario.customers if c.id == updated_vehicle["customerId"]), None)
                if customer and customer.awaitingService is False:
                    print(f"Cannot assign customer to vehicle {vehicle_id}, customer is not awaiting service")
                    non_updated_vehicles.append(vehicle_id)
                    continue
                vehicle.customerId = updated_vehicle["customerId"]
                vehicle.remainingTravelTime = calculate_remaining_travel_time(
                    vehicle.coordX, vehicle.coordY, customer.coordX, customer.coordY, vehicle_travel_speed
                )
            vehicle.vehicleSpeed = vehicle_travel_speed
            updated_vehicles.append(vehicle.to_dict())

        return jsonify({"updatedVehicles": updated_vehicles}) \
            if non_updated_vehicles.__len__() == 0 \
            else jsonify({"failedToUpdate": non_updated_vehicles, "updatedVehicles": updated_vehicles})

parser.remove_argument("db_scenario_id")
parser.add_argument(
    'speed',
    type=float,
    required=False,
    default=0.2,
    help='Execution speed of the scenario (float, set to 1 for real time, < 1 for faster execution)',
    location='args'
)
@scenarioRunnerApi.route('/launch_scenario/<string:scenario_id>')
class LaunchScenario(Resource):
    @api.expect(parser)
    def post(self, scenario_id):
        args = parser.parse_args()
        scenario = scenarios.get(scenario_id)
        speed = args.get('speed', 0.2)
        if not scenario:
            return {"message": "Scenario not found"}, 404

        scenario.status = 'RUNNING'
        scenario.startTime = datetime.now().isoformat()
        scenario_metadata = create_scenario_metadata(scenario)

        # Start a background thread to check vehicle statuses
        threading.Thread(target=self.check_vehicle_statuses, args=(scenario, scenario_metadata, speed), daemon=True).start()

        return jsonify({"message": "Scenario launched successfully", "scenario_id": scenario_id, "startTime": scenario.startTime})


    def check_vehicle_statuses(self, scenario, scenario_metadata, speed):
        for vehicle in scenario.vehicles:
            vehicle_data = VehicleData(id=vehicle.id, travel_times=str(vehicle.remainingTravelTime))
            scenario_metadata.vehicle_data.append(vehicle_data)
        while True:
            for vehicle in scenario.vehicles:
                if vehicle.customerId:
                    if vehicle.remainingTravelTime is not None and vehicle.isAvailable is True:
                        vehicle.isAvailable = False
                        threading.Thread(target=self.executeRoute, args=(vehicle, scenario, scenario_metadata, speed), daemon=True).start()
                    elif vehicle.remainingTravelTime is None and vehicle.isAvailable is True:
                        print(f"Vehicle {vehicle.id} is waiting for remaining travel time to be set.")

            # Check if all customers are done awaiting service
            if all(not customer.awaitingService for customer in scenario.customers):
                scenario.status = 'COMPLETED'
                scenario.endTime = datetime.now().isoformat()
                scenario_metadata.end_time = scenario.endTime
                scenario_metadata.status = scenario.status
                session.merge(scenario_metadata)
                session.commit()
                print(f"Scenario {scenario.id} is now completed, all customers are done awaiting service.")
                break

            time.sleep(2)  # Check every 2 seconds (adjust as needed)


    def executeRoute(self, vehicle, scenario, scenario_metadata, speed):

        # Simulate countdown (for example purposes)
        print(f"Vehicle {vehicle.id} is now unavailable. Remaining travel time: {vehicle.remainingTravelTime} seconds.\n")
        
        # Find the customer associated with the vehicle
        customer = next((c for c in scenario.customers if c.id == vehicle.customerId), None)
        vehicle_metadata = next((v for v in scenario_metadata.vehicle_data if v.id == vehicle.id), None)
        vehicle_metadata.travel_times = vehicle_metadata.travel_times + "," + str(vehicle.remainingTravelTime)
        session.merge(scenario_metadata)
        vehicle.activeTime += vehicle.remainingTravelTime
        for remaining_time in range(vehicle.remainingTravelTime, 0, -1):
            vehicle.remainingTravelTime = remaining_time
            time.sleep(speed)  # Simulate time passage (adjust as needed)

        # Update vehicle and customer after countdown
        if customer:
            # Update vehicle's coordinates to match customer's
            vehicle.coordX = customer.coordX
            vehicle.coordY = customer.coordY
            print(f"Vehicle {vehicle.id} moved to customer's location: ({customer.coordX}, {customer.coordY}).")

            vehicle.remainingTravelTime = (calculate_remaining_travel_time
                    (vehicle.coordX, vehicle.coordY, customer.destinationX, customer.destinationY, vehicle.vehicleSpeed))
            vehicle.activeTime += vehicle.remainingTravelTime
            vehicle_metadata.travel_times = vehicle_metadata.travel_times + "," + str(vehicle.remainingTravelTime)
            session.merge(scenario_metadata)
            print(f"Vehicle {vehicle.id} is now en route to destination: ({customer.destinationX}, {customer.destinationY}).")
            for remaining_time in range(vehicle.remainingTravelTime, 0, -1):
                vehicle.remainingTravelTime = remaining_time
                time.sleep(speed)

            # Unset customerId and mark vehicle as available
            vehicle.customerId = None
            vehicle.isAvailable = True
            vehicle.distanceTravelled += calculate_distance(vehicle.coordX, vehicle.coordY, customer.destinationX, customer.destinationY)
            vehicle.coordX = customer.destinationX
            vehicle.coordY = customer.destinationY
            vehicle.remainingTravelTime = None
            vehicle.vehicleSpeed = 0
            vehicle.numberOfTrips += 1
            print(f"Vehicle {vehicle.id} is now available again.")

            # Update customer's awaitingService status
            customer.awaitingService = False
            customer.coordX = customer.destinationX
            customer.coordY = customer.destinationY
            print(f"Customer {customer.id} is no longer awaiting service.")


def create_scenario_metadata(scenario):
    scenario = ScenarioMetadata(id=scenario.id, start_time=scenario.startTime, end_time=scenario.endTime, status=scenario.status)
    return scenario


def is_valid_uuid(uuid_to_test):
    try:
        uuid.UUID(uuid_to_test)
        return True
    except ValueError:
        return False


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8090, debug=True)
