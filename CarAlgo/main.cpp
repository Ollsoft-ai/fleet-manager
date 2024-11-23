#include "TreeGenerator.h"
#include <chrono>
#include <iostream>

int main() {
    // Create a timer
    auto start = std::chrono::high_resolution_clock::now();

    // Create an instance of TreeGenerator
    TreeGenerator generator;
    
    // Call generateTrees on the instance
    auto trees = generator.generateTrees(123455);

    // Stop timer and calculate duration
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);

    // Print execution time (fixing the format specifier)
    printf("Execution time: %ld milliseconds\n", duration.count());
    // Or use cout:
    // std::cout << "Execution time: " << duration.count() << " milliseconds\n";

    return 0;
}