#include "TreeGenerator.h"
#include "CustomerGenerator.h"
#include "Algorithm.h"
#include <chrono>
#include <iostream>

int main() {
    // Create a timer
    auto start = std::chrono::high_resolution_clock::now();

    // Create an instance of TreeGenerator
    //TreeGenerator Treegenerator;
    
    // Call generateTrees on the instance
    //auto trees = generator.generateTrees(123455);
    CustomerGenerator generator;
    auto customers = generator.generateCustomers(200);
    std::vector<Customer> ignore_list = {};
    ignore_list.push_back(customers[0]);
    Vehicle vehicle0(48.15, 11.5, "vehicle_1", "some customer", 0);
    Vehicle vehicle1(48.17, 11.45, "vehicle_2", "some customer", 0);
    Vehicle vehicle2(48.13, 11.4, "vehicle_3", "some customer", 0);
    std::vector<Vehicle> vics = {};
    vics.push_back(vehicle0);
    vics.push_back(vehicle1);
    vics.push_back(vehicle2);

    Algorithm algo;
    std::map<std::string, std::vector<std::string>> response = algo.assignNextCustomers(customers, vics, 0.0015);

    // Stop timer and calculate duration
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);

    // Print execution time (fixing the format specifier)
    printf("Execution time: %ld milliseconds\n", duration.count());
    for(const auto& [vehicle_id, assignments] : response) {
        std::cout << "Vehicle " << vehicle_id << " assignments:\n";
        for(const auto& assignment : assignments) {
            std::cout << "  " << assignment << "\n";
        }
    }

    printf("\n Excluded:  ");

    for(const auto& str : ignore_list) {
        std::cout << str.id << " ";
    }
    
    std::cout << std::endl;
    // Or use cout:
    // std::cout << "Execution time: " << duration.count() << " milliseconds\n";

    return 0;
}