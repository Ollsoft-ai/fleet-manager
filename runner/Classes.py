from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.event import listens_for
from sqlalchemy.orm import relationship

from DbConfig import Base, engine


# Define the Scenario, Vehicle, and Customer classes
class Vehicle:
    def __init__(self, id, coordX, coordY, vehicleSpeed=None, isAvailable=None, customerId=None, remainingTravelTime=None,
                 distanceTravelled=None, activeTime=None, numberOfTrips=None):
        self.id = id
        self.coordX = coordX
        self.coordY = coordY
        self.vehicleSpeed = vehicleSpeed
        self.isAvailable = isAvailable
        self.customerId = customerId
        self.remainingTravelTime = remainingTravelTime
        self.distanceTravelled = distanceTravelled
        self.activeTime = activeTime
        self.numberOfTrips = numberOfTrips

    def to_dict(self):
        return {
            "id": self.id,
            "coordX": self.coordX,
            "coordY": self.coordY,
            "vehicleSpeed": self.vehicleSpeed,
            "isAvailable": self.isAvailable,
            "customerId": self.customerId,
            "remainingTravelTime": self.remainingTravelTime,
            "distanceTravelled": self.distanceTravelled,
            "activeTime": self.activeTime,
            "numberOfTrips": self.numberOfTrips
        }

class Customer:
    def __init__(self, id, coordX, coordY, destinationX, destinationY, awaitingService=None):
        self.id = id
        self.coordX = coordX
        self.coordY = coordY
        self.destinationX = destinationX
        self.destinationY = destinationY
        self.awaitingService = awaitingService

    def to_dict(self):
        return {
            "id": self.id,
            "coordX": self.coordX,
            "coordY": self.coordY,
            "destinationX": self.destinationX,
            "destinationY": self.destinationY,
            "awaitingService": self.awaitingService
        }

class Scenario:
    def __init__(self, id, startTime=None, endTime=None, status=None):
        self.id = id
        self.startTime = startTime
        self.endTime = endTime
        self.status = status
        self.vehicles = []
        self.customers = []

    def add_vehicle(self, vehicle_data):
        vehicle = Vehicle(**vehicle_data)
        self.vehicles.append(vehicle)

    def add_customer(self, customer_data):
        customer = Customer(**customer_data)
        self.customers.append(customer)

    def to_dict(self):
        return {
            "id": self.id,
            "startTime": self.startTime,
            "endTime": self.endTime,
            "status": self.status,
            "vehicles": [vehicle.to_dict() for vehicle in self.vehicles],
            "customers": [customer.to_dict() for customer in self.customers]
        }


class ScenarioMetadata(Base):
    __tablename__ = "scenario_metadata"

    id = Column(String, primary_key=True)
    start_time = Column(String)
    end_time = Column(String)
    status = Column(String)
    vehicle_data = relationship("VehicleData", back_populates="scenario", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "startTime": self.start_time,
            "endTime": self.end_time,
            "status": self.status,
            "vehicleData": [vehicle.to_dict() for vehicle in self.vehicle_data],
        }


class VehicleData(Base):
    __tablename__ = "vehicle_data"

    id = Column(String, primary_key=True)
    travel_times = Column(String)
    total_trips = Column(Integer, default=0)
    total_travel_time = Column(Integer, default=0)
    scenario_id = Column(String, ForeignKey("scenario_metadata.id"))
    scenario = relationship("ScenarioMetadata", back_populates="vehicle_data")

    def get_travel_times(self):
        return list(map(float, self.travel_times.split(','))) if self.travel_times else []

    def to_dict(self):
        return {
            "id": self.id,
            "travelTimes": self.get_travel_times(),
            "totalTrips": self.total_trips,
            "totalTravelTime": self.total_travel_time,
        }

@listens_for(VehicleData.travel_times, "set", retval=False)
def update_totals(target, value, oldvalue, initiator):
    if value == 'None':
        return
    if value != oldvalue:
        value = value.replace("None", "").replace(", ,", ",").strip(',')
        travel_times_list = [entry for entry in map(float, value.split(',')) if entry != 0] if value else []
        target.total_trips = (len(travel_times_list) / 2).__int__()
        target.total_travel_time = sum(travel_times_list).__int__()

Base.metadata.create_all(engine)

    