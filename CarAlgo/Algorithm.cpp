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
    std::vector<Vehicle> unassigned_vehicles(vehicles);

    // Keep trying to assign until all vehicles are assigned or no more possibilities
    while (!unassigned_vehicles.empty()) {
        bool any_assignment_made = false;

        // Try to assign customers to each unassigned vehicle
        for (auto it = unassigned_vehicles.begin(); it != unassigned_vehicles.end();) {
            auto result = giveNextBestCustomers(customer_list, *it, radius_threshold, global_ignore_list);
            
            if (!result.empty()) {  // Accept even single customer assignments
                std::vector<std::string> customer_ids;
                float total_weight = 0;

                // Always add first customer
                customer_ids.push_back(result[0].id);
                total_weight += result[0].weight;

                // Add second customer if available
                if (result.size() >= 2) {
                    customer_ids.push_back(result[1].id);
                    total_weight += result[1].weight;
                }

                assignments[it->id] = customer_ids;
                total_weights[it->id] = total_weight;

                // Add first customer to global ignore list
                auto first_customer = std::find_if(customer_list.begin(), customer_list.end(),
                    [&result](const Customer& c) { return c.id == result[0].id; });
                if (first_customer != customer_list.end()) {
                    global_ignore_list.push_back(*first_customer);
                }

                // Remove this vehicle from unassigned list
                it = unassigned_vehicles.erase(it);
                any_assignment_made = true;
            } else {
                ++it;
            }
        }

        if (!any_assignment_made) {
            // If we couldn't make any assignments, try with increased radius
            radius_threshold *= 1.5;
            std::cout << "Increasing radius threshold to: " << radius_threshold << std::endl;

            // If radius gets too large, break to avoid infinite loop
            if (radius_threshold > 0.1) {
                break;
            }
            continue;
        }

        // Resolve conflicts
        bool changes_made;
        do {
            changes_made = false;
            std::map<std::string, std::vector<Vehicle>> customer_vehicles;

            // Find conflicts
            for (const auto& pair : assignments) {
                const std::string& vid = pair.first;
                const std::vector<std::string>& assigned_customers = pair.second;

                if (!assigned_customers.empty()) {
                    auto vehicle_it = std::find_if(vehicles.begin(), vehicles.end(),
                        [&vid](const Vehicle& v) { return v.id == vid; });

                    if (vehicle_it != vehicles.end()) {
                        customer_vehicles[assigned_customers[0]].push_back(*vehicle_it);
                    }
                }
            }

            // Resolve conflicts
            for (const auto& pair : customer_vehicles) {
                const std::string& customer_id = pair.first;
                const std::vector<Vehicle>& competing_vehicles = pair.second;

                if (competing_vehicles.size() > 1) {
                    auto max_weight_vehicle = std::max_element(
                        competing_vehicles.begin(), competing_vehicles.end(),
                        [&total_weights](const Vehicle& a, const Vehicle& b) {
                            return total_weights[a.id] < total_weights[b.id];
                        });

                    if (max_weight_vehicle != competing_vehicles.end()) {
                        std::vector<Customer> local_ignore_list = global_ignore_list;

                        // Add contested customer to ignore list
                        for (const auto& cust : customer_list) {
                            if (cust.id == customer_id) {
                                local_ignore_list.push_back(cust);
                                break;
                            }
                        }

                        auto new_result = giveNextBestCustomers(
                            customer_list,
                            *max_weight_vehicle,
                            radius_threshold,
                            local_ignore_list);

                        if (!new_result.empty()) {
                            std::vector<std::string> new_customer_ids;
                            float total_weight = 0;

                            new_customer_ids.push_back(new_result[0].id);
                            total_weight += new_result[0].weight;

                            if (new_result.size() >= 2) {
                                new_customer_ids.push_back(new_result[1].id);
                                total_weight += new_result[1].weight;
                            }

                            assignments[max_weight_vehicle->id] = new_customer_ids;
                            total_weights[max_weight_vehicle->id] = total_weight;
                            changes_made = true;
                        }
                    }
                }
            }
        } while (changes_made);
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
    std::vector<CustomerOption> result = findNextBestOption(root, ignore_list);
    return result;
}