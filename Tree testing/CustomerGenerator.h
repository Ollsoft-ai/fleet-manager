#pragma once
#include <vector>
#include "Customer.h"

class CustomerGenerator {
public:
    float minLat, maxLat, minLon, maxLon;

    CustomerGenerator(float latMin = 48.1, float latMax = 48.2, 
                     float lonMin = 11.4, float lonMax = 11.6);
    std::vector<Customer> generateCustomers(int numCustomers);
};