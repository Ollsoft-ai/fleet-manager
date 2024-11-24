#pragma once
#include <vector>
#include <string>
#include <memory>

class TreeNode : public std::enable_shared_from_this<TreeNode> {
public:
    std::string name;
    const float weight;
    std::weak_ptr<TreeNode> parent;
    std::vector<std::shared_ptr<TreeNode>> children;

    TreeNode(const std::string& nodeName, const float weight);
    void addChild(std::shared_ptr<TreeNode> child);
    std::vector<std::shared_ptr<TreeNode>> getChildren(std::shared_ptr<TreeNode> root);
};