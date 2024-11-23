#pragma once
#include <map>
#include "Customer.h"
#include "TreeNode.h"

class TreeGenerator {
public:
    std::map<std::string, std::shared_ptr<TreeNode>> generateTrees(int scenarioId);

private:
    void printTree(std::shared_ptr<TreeNode> node, std::string prefix = "");
    float getWeight(const Customer& custPrev, const Customer& custNext);
    float getWeightVehicle(double vehicleX, double vehicleY, const Customer& custNext);
    double getDistance(double x1, double y1, double x2, double y2);
    void makeChildren(std::shared_ptr<TreeNode> root,
                     const Customer& currCust,
                     std::vector<Customer>& remainingCust,
                     int depth);
    void makeChildrenVehicle(std::shared_ptr<TreeNode> root,
                     const double vehicleX,
                     const double vehicleY,
                     std::vector<Customer>& remainingCust,
                     int depth);
};