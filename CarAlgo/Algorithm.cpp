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
    std::map<std::string, float> total_weights;
    std::vector<Customer> global_ignore_list;
    
    // Debug print
    std::cout << "\nProcessing " << vehicles.size() << " vehicles\n";

    // First pass: Get initial assignments for all vehicles
    for(const auto& vehicle : vehicles) {
        std::cout << "\nProcessing vehicle: " << vehicle.id << std::endl;
        
        auto result = giveNextBestCustomers(customer_list, vehicle, radius_threshold, global_ignore_list);
        if(result.size() >= 2) {
            std::vector<std::string> customer_ids = {result[0].id, result[1].id};
            assignments[vehicle.id] = customer_ids;
            total_weights[vehicle.id] = result[0].weight + result[1].weight;
            
            // Add only the first customer to global ignore list
            auto first_customer = std::find_if(customer_list.begin(), customer_list.end(),
                [&result](const Customer& c) { return c.id == result[0].id; });
            if(first_customer != customer_list.end()) {
                global_ignore_list.push_back(*first_customer);
            }
        }
    }

    bool changes_made;
    do {
        changes_made = false;
        std::map<std::string, std::vector<Vehicle>> customer_vehicles;
        
        // Find conflicts
        for(const auto& pair : assignments) {
            const std::string& vid = pair.first;
            const std::vector<std::string>& assigned_customers = pair.second;
            
            if(!assigned_customers.empty()) {
                auto vehicle_it = std::find_if(vehicles.begin(), vehicles.end(),
                    [&vid](const Vehicle& v) { return v.id == vid; });
                
                if(vehicle_it != vehicles.end()) {
                    customer_vehicles[assigned_customers[0]].push_back(*vehicle_it);
                }
            }
        }

        // Print conflicts
        std::cout << "\nChecking for conflicts:\n";
        for(const auto& pair : customer_vehicles) {
            std::cout << "Customer " << pair.first << " is assigned to " 
                     << pair.second.size() << " vehicles\n";
        }

        // Resolve conflicts
        for(const auto& pair : customer_vehicles) {
            const std::string& customer_id = pair.first;
            const std::vector<Vehicle>& competing_vehicles = pair.second;
            
            if(competing_vehicles.size() > 1) {
                std::cout << "\nResolving conflict for customer: " << customer_id << std::endl;
                
                auto max_weight_vehicle = std::max_element(
                    competing_vehicles.begin(), competing_vehicles.end(),
                    [&total_weights](const Vehicle& a, const Vehicle& b) {
                        return total_weights[a.id] < total_weights[b.id];
                    });

                if(max_weight_vehicle != competing_vehicles.end()) {
                    std::cout << "Vehicle " << max_weight_vehicle->id 
                             << " needs new assignment\n";
                    
                    std::vector<Customer> local_ignore_list = global_ignore_list;
                    
                    // Add the contested customer to ignore list
                    for(const auto& cust : customer_list) {
                        if(cust.id == customer_id) {
                            local_ignore_list.push_back(cust);
                            break;
                        }
                    }

                    auto new_result = giveNextBestCustomers(
                        customer_list, 
                        *max_weight_vehicle, 
                        radius_threshold,
                        local_ignore_list);

                    if(new_result.size() >= 2) {
                        std::vector<std::string> new_customer_ids = {new_result[0].id, new_result[1].id};
                        assignments[max_weight_vehicle->id] = new_customer_ids;
                        total_weights[max_weight_vehicle->id] = new_result[0].weight + new_result[1].weight;
                        changes_made = true;
                    }
                }
            }
        }
    } while(changes_made);

    // Print final assignments with weights
    std::cout << "\nFinal Assignments:\n";
    for(const auto& pair : assignments) {
        const std::string& vid = pair.first;
        const std::vector<std::string>& assigned_customers = pair.second;
        
        std::cout << "Vehicle " << vid << " (total weight: " << total_weights[vid] << "):\n";
        for(const auto& cid : assigned_customers) {
            std::cout << "  Customer: " << cid << "\n";
        }
    }

    return assignments;
}

std::vector<CustomerOption> Algorithm::findNextBestOption(std::shared_ptr<TreeNode> root, std::vector<Customer> ignore_list){
    int option_found = 0;
    std::vector<CustomerOption> output = {};
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
                output.push_back(CustomerOption(child_name, current_children[i]->weight));
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

//TODO: MAke radius threshohold do smth
std::vector<CustomerOption> Algorithm::giveNextBestCustomers(std::vector<Customer> customer_list, Vehicle vehicle, double radius_threshhold, std::vector<Customer> ignore_list) {
    TreeGenerator treeGenerator;
    auto root = std::make_shared<TreeNode>(vehicle.id, 0.0f);
    treeGenerator.makeChildrenVehicle(root, vehicle.coordX,vehicle.coordY,customer_list, 0, 2);
    std::cout << "\nVehicle Tree Structure:\n";
    treeGenerator.printTree(root); 
    std::vector<CustomerOption> result = findNextBestOption(root, ignore_list);
    return result;
}