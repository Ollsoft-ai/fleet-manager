#pragma once
#include "Customer.h"
#include "Vehicle.h"
#include <vector>
#include <string>
#include <map>
#include "TreeNode.h"
#include "TreeGenerator.h"

struct CustomerOption {
    std::string id;
    float weight;

    CustomerOption(std::string customer_id, float customer_weight) 
            : id(customer_id), weight(customer_weight) {}
};

class Algorithm {
public:
    std::map<std::string, std::vector<std::string>> assignNextCustomers(
        const std::vector<Customer>& customer_list,
        const std::vector<Vehicle>& vehicles,
        double radius_threshold);
    static std::vector<CustomerOption> findNextBestOption(std::shared_ptr<TreeNode> root, 
                                                      std::vector<Customer> ignore_list);
    static std::vector<CustomerOption> giveNextBestCustomers(std::vector<Customer> customers, 
                                                         Vehicle vehicle, 
                                                         double maxDistance,
                                                         std::vector<Customer> ignore_list);
private:
    double calculateTotalDistance(const Vehicle& vehicle, 
                                const Customer& first, 
                                const Customer& second);
};