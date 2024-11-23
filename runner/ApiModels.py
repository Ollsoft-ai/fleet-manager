from flask import Flask
from flask_restx import Api, fields

app = Flask(__name__)
api = Api(app, version="1.0", title="ScenarioRunner API", description="A simple API for managing scenarios")

# Define API Models for automatic documentation
vehicle_model = api.model('Vehicle', {
    'id': fields.String(required=True, description="Vehicle ID"),
    'coordX': fields.Float(required=True, description="X Coordinate of the vehicle"),
    'coordY': fields.Float(required=True, description="Y Coordinate of the vehicle"),
    'isAvailable': fields.Boolean(description="Availability of the vehicle"),
    'vehicleSpeed': fields.Float(description="Speed of the vehicle"),
    'customerId': fields.String(description="ID of the customer assigned to the vehicle"),
    'remainingTravelTime': fields.Float(description="Remaining travel time for the vehicle"),
    'distanceTravelled': fields.Float(description="Total distance the vehicle has travelled"),
    'activeTime': fields.Float(description="Total active time of the vehicle"),
    'numberOfTrips': fields.Integer(description="Total number of trips made by the vehicle")
})

vehicle_update_model = api.model('VehicleUpdate', {
    'id': fields.String(required=True, description="Vehicle ID"),
    'customerId': fields.String(description="Assigned customer ID")
})

customer_model = api.model('Customer', {
    'id': fields.String(required=True, description="Customer ID"),
    'coordX': fields.Float(description="Customer X coordinate"),
    'coordY': fields.Float(description="Customer Y coordinate"),
    'destinationX': fields.Float(description="Customer destination X coordinate"),
    'destinationY': fields.Float(description="Customer destination Y coordinate"),
    'awaitingService': fields.Boolean(description="Whether the customer is awaiting service")
})

scenario_model = api.model('Scenario', {
    'id': fields.String(required=True, description="Scenario ID"),
    'startTime': fields.String(description="Start time of the scenario"),
    'endTime': fields.String(description="End time of the scenario"),
    'status': fields.String(description="Status of the scenario"),
    'vehicles': fields.List(fields.Nested(vehicle_model), description="List of vehicles"),
    'customers': fields.List(fields.Nested(customer_model), description="List of customers")
})

update_scenario_model = api.model('UpdateScenario', {
    'vehicles': fields.List(fields.Nested(vehicle_update_model), description="List of updated vehicles"),
})