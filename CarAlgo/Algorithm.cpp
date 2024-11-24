#include "Algorithm.h"
#include <cmath>
#include <algorithm>

double calculateDistance(double x1, double y1, double x2, double y2) {
    return std::sqrt(std::pow(x2 - x1, 2) + std::pow(y2 - y1, 2));
}

double Algorithm::calculateTotalDistance(const Vehicle& vehicle, 
                                      const Customer& first, 
                                      const Customer& second) {
    double d1 = calculateDistance(vehicle.coordX, vehicle.coordY, first.coordX, first.coordY);
    double d2 = calculateDistance(first.coordX, first.coordY, second.coordX, second.coordY);
    return d1 + d2;
}

std::map<std::string, std::vector<std::string>> Algorithm::assignNextCustomers(
    const std::vector<Customer>& customer_list,
    const std::vector<Vehicle>& vehicles,
    double radius_threshold) 
{
    std::map<std::string, std::vector<std::string>> assignments;
    return assignments;
}