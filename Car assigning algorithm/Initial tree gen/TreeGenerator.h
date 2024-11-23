#pragma once
#include <map>
#include "Customer.h"
#include "TreeNode.h"

class TreeGenerator {
public:
    static double getWeight(const Customer& custPrev, const Customer& custNext);
    static const std::vector<Customer>& makeChildren(std::shared_ptr<TreeNode> root, 
                           const Customer& currCust,
                           const std::vector<Customer>& remainingCust,
                           int depth);
    static std::map<std::string, std::shared_ptr<TreeNode>> generateTrees(int scenarioId);
    static void printTree(std::shared_ptr<TreeNode> node, std::string prefix = "");
};