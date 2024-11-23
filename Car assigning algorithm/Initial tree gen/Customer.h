#pragma once
#include <string>

class Customer {
public:
    float coordX;
    float coordY;
    float destinationX;
    float destinationY;
    std::string id;
    bool awaitingService;

    Customer(float cX, float cY, float dX, float dY, std::string customerId, bool awaiting = false);
    static Customer createRandom(float minLat = 48.1, float maxLat = 48.2, 
                               float minLon = 11.4, float maxLon = 11.6);
};
