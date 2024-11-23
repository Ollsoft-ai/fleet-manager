#pragma once
#include "TreeGenerator.h" 
#include "Customer.h"
#include "Vehicle.h"
#include <vector>
#include <string>  // Add these two includes

class Algorithm {
private:
    TreeGenerator treeGenerator;

public:
    std::vector<std::string> giveNextBestCustomers(std::vector<Customer> customer_list, 
                                                  Vehicle vehicle, 
                                                  double radius_threshhold);
};