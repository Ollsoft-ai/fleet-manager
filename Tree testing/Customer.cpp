#include "Customer.h"
#include <random>
#include <uuid/uuid.h> // You'll need a UUID library, or you can implement your own ID generation

std::string uuid_generate() {
    uuid_t uuid;
    char uuid_str[37];
    uuid_generate(uuid);
    uuid_unparse_lower(uuid, uuid_str);
    return std::string(uuid_str);
}

Customer::Customer(float cX, float cY, float dX, float dY, std::string customerId, bool awaiting)
    : coordX(cX), coordY(cY), destinationX(dX), destinationY(dY), 
      id(customerId), awaitingService(awaiting) {}

Customer Customer::createRandom(float minLat, float maxLat, float minLon, float maxLon) {
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> latDist(minLat, maxLat);
    std::uniform_real_distribution<> lonDist(minLon, maxLon);

    // Generate UUID (implementation depends on your UUID library)
    std::string uuid = uuid_generate(); // You'll need to implement this

    return Customer(
        latDist(gen),  // coordX
        lonDist(gen),  // coordY
        latDist(gen),  // destinationX
        lonDist(gen),  // destinationY
        uuid
    );
}