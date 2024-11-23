#include "TreeGenerator.h"
#include <iostream>
#include <chrono>

int main() {
    // Start timer
    auto start_time = std::chrono::high_resolution_clock::now();
    
    printf("start\n");
    auto trees = TreeGenerator::generateTrees(123455);
    printf("done\n");
    
    // End timer and calculate duration
    auto end_time = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time);
    
    printf("Execution time: %lld milliseconds\n", duration.count());
    return 0;
}