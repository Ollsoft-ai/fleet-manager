#include "TreeGenerator.h"
#include "CustomerGenerator.h"
#include <cmath>
#include <iostream>
#include <algorithm>  // Add this for copy_if


void TreeGenerator::printTree(std::shared_ptr<TreeNode> node, std::string prefix) {
    std::cout << prefix << node->name << std::endl;
    for (const auto& child : node->children) {
        printTree(child, prefix + "  ");
    }
}

double TreeGenerator::getWeight(const Customer& custPrev, const Customer& custNext) {
    double dx = custPrev.destinationX - custNext.coordX;
    double dy = custPrev.destinationY - custNext.coordY;
    return std::sqrt(dx * dx + dy * dy);
}

// Helper function to get distance between two points
double getDistance(double x1, double y1, double x2, double y2) {
    double dx = x2 - x1;
    double dy = y2 - y1;
    return std::sqrt(dx * dx + dy * dy);
}

const std::vector<Customer>& TreeGenerator::makeChildren(std::shared_ptr<TreeNode> root,
                               const Customer& currCust,
                               const std::vector<Customer>& remainingCust,
                               int depth) {
    if (remainingCust.empty() || depth >= 2) return remainingCust;

    // Define distance threshold (adjust this value as needed)
    const double DISTANCE_THRESHOLD = 0.015; // About 5km in decimal degrees

    // Filter close customers
    std::vector<Customer> closeCustomers;
    bool someone_found = false;
    for (const auto& customer : remainingCust) {
        double distance = getDistance(currCust.destinationX, currCust.destinationY,
                                    customer.coordX, customer.coordY);
        if (distance <= DISTANCE_THRESHOLD) {
            closeCustomers.push_back(customer);
        }
    }

    // Create nodes only for close customers
    for (const auto& customer : closeCustomers) {
        double weight = getWeight(currCust, customer);
        std::string nodeName = customer.id + "_" + std::to_string(weight);
        auto customerNode = std::make_shared<TreeNode>(nodeName);
        root->addChild(customerNode);

        // Create new remaining customers vector without current customer
        std::vector<Customer> newRemaining;
        for (const auto& c : remainingCust) {
            if (c.id != customer.id) {
                newRemaining.push_back(c);
            }
        }

        makeChildren(customerNode, customer, newRemaining, depth +1);
    }
}

std::map<std::string, std::shared_ptr<TreeNode>> TreeGenerator::generateTrees(int scenarioId) {
    CustomerGenerator generator;
    auto customers = generator.generateCustomers(200);
    std::map<std::string, std::shared_ptr<TreeNode>> customerTrees;

    for (const auto& customer : customers) {
        auto root = std::make_shared<TreeNode>(customer.id + "_0");
        
        // Create remaining customers vector without current customer
        std::vector<Customer> remaining;
        for (const auto& c : customers) {
            if (c.id != customer.id) {
                remaining.push_back(c);
            }
        }

        remaining = makeChildren(root, customer, remaining, 0);
        customerTrees[customer.id] = root, remaining;

        std::cout << "\nCustomer " << customer.id << " tree:\n";
        printTree(root);
    }

    return customerTrees;
}