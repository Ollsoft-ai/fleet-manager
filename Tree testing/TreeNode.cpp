#include "TreeNode.h"

TreeNode::TreeNode(const std::string& nodeName) : name(nodeName) {}

void TreeNode::addChild(std::shared_ptr<TreeNode> child) {
    child->parent = shared_from_this();
    children.push_back(child);
}