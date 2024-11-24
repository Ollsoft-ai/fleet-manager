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
    auto customers = generator.generateCustomers(20);
    std::vector<Customer> ignore_list = {};
    ignore_list.push_back(customers[0]);
    Vehicle vehicle(48.15, 11.5, "vehicle_1", "some customer", 0);

    Algorithm algo;
    std::vector<std::string> response = algo.giveNextBestCustomers(customers, vehicle, 0.0015, ignore_list);

    // Stop timer and calculate duration
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);

    // Print execution time (fixing the format specifier)
    printf("Execution time: %ld milliseconds\n", duration.count());
    for(const auto& str : response) {
        std::cout << str << " ";
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