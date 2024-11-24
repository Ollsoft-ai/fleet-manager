#pragma once
#include "Customer.h"
#include "Vehicle.h"
#include <vector>
#include <string>
#include <map>

class Algorithm {
public:
    std::map<std::string, std::vector<std::string>> assignNextCustomers(
        const std::vector<Customer>& customer_list,
        const std::vector<Vehicle>& vehicles,
        double radius_threshold);
private:
    double calculateTotalDistance(const Vehicle& vehicle, 
                                const Customer& first, 
                                const Customer& second);
    static std::vector<std::string> findNextBestOption(std::shared_ptr<TreeNode> root, 
                                                      std::vector<Customer> ignore_list);
    static std::vector<std::string> giveNextBestCustomers(std::vector<Customer> customers, 
                                                         Vehicle vehicle, 
                                                         double maxDistance,
                                                         std::vector<Customer> ignore_list);
};