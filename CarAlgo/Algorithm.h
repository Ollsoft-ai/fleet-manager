#pragma once
#include "TreeGenerator.h" 
#include "Customer.h"
#include "Vehicle.h"
#include <vector>
#include <string>  // Add these two includes

class Algorithm {
public:
    static std::vector<std::string> findNextBestOption(std::shared_ptr<TreeNode> root, 
                                                      std::vector<Customer> ignore_list);
    static std::vector<std::string> giveNextBestCustomers(std::vector<Customer> customers, 
                                                         Vehicle vehicle, 
                                                         double maxDistance,
                                                         std::vector<Customer> ignore_list);
};