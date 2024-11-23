#pragma once
#include <vector>
#include <string>
#include <memory>

class TreeNode : public std::enable_shared_from_this<TreeNode> {
public:
    std::string name;
    std::weak_ptr<TreeNode> parent;
    std::vector<std::shared_ptr<TreeNode>> children;

    TreeNode(const std::string& nodeName);
    void addChild(std::shared_ptr<TreeNode> child);
};