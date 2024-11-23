#include "Vehicle.h"
#include <random>
#include <uuid/uuid.h> // You'll need a UUID library, or you can implement your own ID generation

std::string uuid_generate() {
    uuid_t uuid;
    char uuid_str[37];
    uuid_generate(uuid);
    uuid_unparse_lower(uuid, uuid_str);
    return std::string(uuid_str);
}

Vehicle::Vehicle(float cX, float cY, std::string id, std::string customer_id, int number_of_trips = 0)
    : coordX(cX), coordY(cY), id(id) ,customer_id(customer_id), number_of_trips(number_of_trips) {}
