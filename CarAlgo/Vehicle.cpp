#include "Vehicle.h"
#include <random>

Vehicle::Vehicle(float cX, float cY, std::string id, std::string customer_id, int number_of_trips)
    : coordX(cX), coordY(cY), id(id) ,customer_id(customer_id), number_of_trips(number_of_trips) {}
