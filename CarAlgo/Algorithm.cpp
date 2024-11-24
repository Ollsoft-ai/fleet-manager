#include "Algorithm.h"
#include <cmath>
#include <algorithm>
#include <vector>
#include <string>
#include <iostream>
#include "TreeNode.h"
#include "TreeGenerator.h"

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

std::vector<std::string> Algorithm::findNextBestOption(std::shared_ptr<TreeNode> root, std::vector<Customer> ignore_list){
    int option_found = 0;
    std::vector<std::string> output = {};
    int i = 0;
    std::vector<std::shared_ptr<TreeNode>> current_children = root->children;
    
    while(option_found <= 1){
        if(i < (int) current_children.size()) {
            std::string child_name = current_children[i]->name;
        
            bool is_ignored = false;
            for(const auto& ignore : ignore_list) {
                if(child_name.find(ignore.id) != std::string::npos) {
                    is_ignored = true;
                    break;
                }
            }
            if(!is_ignored) {
                option_found++;
                output.push_back(child_name);
                if(option_found == 1) {
                    current_children = current_children[i]->children;
                    i = 0;
                    continue;
                } else if (option_found >= 2) {
                    return output;
                }
            }
            i++;
        } else {
            return output;
        }
    }
    return output;
}


std::vector<std::string> Algorithm::giveNextBestCustomers(std::vector<Customer> customer_list, Vehicle vehicle, double radius_threshhold, std::vector<Customer> ignore_list) {
    TreeGenerator treeGenerator;
    auto root = std::make_shared<TreeNode>(vehicle.id, 0.0f);
    treeGenerator.makeChildrenVehicle(root, vehicle.coordX,vehicle.coordY,customer_list, 0, 2);
    std::cout << "\nVehicle Tree Structure:\n";
    treeGenerator.printTree(root); 
    std::vector<std::string> result = findNextBestOption(root, ignore_list);
    return result;
}