#pragma once
#include <string>

class Vehicle {
public:
    float coordX;
    float coordY;
    std::string id;
    std::string customer_id;
    int number_of_trips;

    Vehicle(float cX, float cY, std::string id, std::string customer_id, int number_of_trips);
};
