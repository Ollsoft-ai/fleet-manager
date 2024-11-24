#include "TreeNode.h"
#include <algorithm>

TreeNode::TreeNode(const std::string& nodeName, const float Nodeweight) 
    : name(nodeName), weight(Nodeweight) {}

std::vector<std::shared_ptr<TreeNode>> getChildren(std::shared_ptr<TreeNode> root) {
    return root->children;
}

void TreeNode::addChild(std::shared_ptr<TreeNode> child) {
    child->parent = shared_from_this();  // Change to weak_from_this since parent is weak_ptr
    
    // Find the position to insert based on weight (descending order)
    auto insertPos = std::lower_bound(children.begin(), children.end(), child,
        [](const std::shared_ptr<TreeNode>& a, const std::shared_ptr<TreeNode>& b) {
            return a->weight < b->weight;  // '<' for ascending order
        });
    
    // Insert at the found position
    children.insert(insertPos, child);
}