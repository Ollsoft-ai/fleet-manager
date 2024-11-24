#include "TreeGenerator.h"
#include "CustomerGenerator.h"
#include <cmath>
#include <iostream>
#include <algorithm>

void TreeGenerator::printTree(std::shared_ptr<TreeNode> node, std::string prefix) {
    if (!node) return;
    std::cout << prefix << node->name << " " << node->weight << std::endl;
    for (const auto& child : node->children) {
        printTree(child, prefix + "  ");
    }
}

float TreeGenerator::getWeight(const Customer& custPrev, const Customer& custNext) {
    float dx = custPrev.destinationX - custNext.coordX;
    float dy = custPrev.destinationY - custNext.coordY;
    return std::sqrt(dx * dx + dy * dy);
}

float TreeGenerator::getWeightVehicle(double vehicleX, double vehicleY, const Customer& custNext) {
    float dx = vehicleX - custNext.coordX;
    float dy = vehicleY - custNext.coordY;
    return std::sqrt(dx * dx + dy * dy);
}

double TreeGenerator::getDistance(double x1, double y1, double x2, double y2) {
    double dx = x2 - x1;
    double dy = y2 - y1;
    return std::sqrt(dx * dx + dy * dy);
}

void TreeGenerator::makeChildren(std::shared_ptr<TreeNode> root,
                               const Customer& currCust,
                               std::vector<Customer>& remainingCust,
                               int depth) {
    if (!root || remainingCust.empty() || depth >= 2) return;

    const double DISTANCE_THRESHOLD = 0.015;
    std::vector<Customer> closeCustomers;
    double distThresh = DISTANCE_THRESHOLD;
    
    // Find close customers
    bool someone_found = false;
    while (!someone_found && distThresh <= 0.1) {  // Add upper limit to threshold
        for (const auto& customer : remainingCust) {
            double distance = getDistance(currCust.destinationX, currCust.destinationY,
                                       customer.coordX, customer.coordY);
            if (distance <= distThresh) {
                closeCustomers.push_back(customer);
                someone_found = true;
            }
        }
        distThresh += 0.01;
    }

    // Process close customers
    for (const auto& customer : closeCustomers) {
        float weight = getWeight(currCust, customer);
        auto customerNode = std::make_shared<TreeNode>(customer.id, weight);
        
        if (root) {  // Add null check
            root->addChild(customerNode);
        }

        // Create new remaining customers vector
        std::vector<Customer> newRemaining;
        std::copy_if(remainingCust.begin(), remainingCust.end(),
                    std::back_inserter(newRemaining),
                    [&customer](const Customer& c) { return c.id != customer.id; });

        makeChildren(customerNode, customer, newRemaining, depth + 1);
    }
}

void TreeGenerator::makeChildrenVehicle(std::shared_ptr<TreeNode> root,
                     const double vehicleX,
                     const double vehicleY,
                     std::vector<Customer>& remainingCust,
                     int depth,
                     int desired_depth)
    {
    if (!root || remainingCust.empty() || depth >= 2) return;

    const double DISTANCE_THRESHOLD = 0.015;
    std::vector<Customer> closeCustomers;
    double distThresh = DISTANCE_THRESHOLD;
    
    // Find close customers
    bool someone_found = false;
    while (!someone_found && distThresh <= 0.1) {  // Add upper limit to threshold
        for (const auto& customer : remainingCust) {
            double distance = getDistance(vehicleX, vehicleY,
                                       customer.coordX, customer.coordY);
            if (distance <= distThresh) {
                closeCustomers.push_back(customer);
                someone_found = true;
            }
        }
        distThresh += 0.01;
    }

    // Process close customers
    for (const auto& customer : closeCustomers) {
        float weight = getWeightVehicle(((float) vehicleX), ((float) vehicleY), customer);
        auto customerNode = std::make_shared<TreeNode>(customer.id, weight);
        
        if (root) {  // Add null check
            root->addChild(customerNode);
        }

        // Create new remaining customers vector
        std::vector<Customer> newRemaining;
        std::copy_if(remainingCust.begin(), remainingCust.end(),
                    std::back_inserter(newRemaining),
                    [&customer](const Customer& c) { return c.id != customer.id; });

        makeChildren(customerNode, customer, newRemaining, depth + 1);
    }
}

std::map<std::string, std::shared_ptr<TreeNode>> TreeGenerator::generateTrees(int scenarioId) {
    CustomerGenerator generator;
    auto customers = generator.generateCustomers(200);
    std::map<std::string, std::shared_ptr<TreeNode>> customerTrees;

    for (const auto& customer : customers) {
        auto root = std::make_shared<TreeNode>(customer.id, 0.0f);
        if (!root) continue;  // Add null check

        std::vector<Customer> remaining;
        std::copy_if(customers.begin(), customers.end(),
                    std::back_inserter(remaining),
                    [&customer](const Customer& c) { return c.id != customer.id; });

        makeChildren(root, customer, remaining, 0);
        customerTrees[customer.id] = root;

        std::cout << "\nCustomer " << customer.id << " tree:\n";
        printTree(root);
    }

    return customerTrees;
}