#include "CustomerGenerator.h"

CustomerGenerator::CustomerGenerator(float latMin, float latMax, float lonMin, float lonMax)
    : minLat(latMin), maxLat(latMax), minLon(lonMin), maxLon(lonMax) {}

std::vector<Customer> CustomerGenerator::generateCustomers(int numCustomers) {
    std::vector<Customer> customers;
    for (int i = 0; i < numCustomers; i++) {
        customers.push_back(Customer::createRandom(minLat, maxLat, minLon, maxLon));
    }
    return customers;
}