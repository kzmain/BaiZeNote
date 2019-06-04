import json
import os

from Tree.NoteNode import NoteNode
from Tree.NoteRootNode import NoteRootNode


class NoteTree:
    node_id = 0
    current_node = None
    tree_nodes_dict = {}

    def __init__(self):
        self.tree_nodes_dict = {}
        self.current_node = None
        self.node_id = 0

    def add_child_node(self, node_name, md_section_info_dict):
        if self.current_node is None and len(self.tree_nodes_dict) == 0:
            node = NoteRootNode()
            node.nodeId = self.node_id
            node.parentNodeId = None
        elif self.current_node is None and len(self.tree_nodes_dict) > 0:
            raise Exception
        else:
            node = NoteNode()
            node.name = node_name
            node.nodeId = self.node_id
            node.parentNodeId = self.current_node.nodeId
            self.current_node.childNodesIds.append(node.nodeId)
        node.section_dict = md_section_info_dict["section"]
        node.md_dict = md_section_info_dict["md"]
        node.relative_path = md_section_info_dict["section_path_relative"]
        self.tree_nodes_dict[self.node_id] = node
        self.node_id += 1
        return

    def go_to_node(self, node_id):
        self.current_node = self.tree_nodes_dict[node_id]
        return self.current_node

    def go_to_parent_node(self):
        if self.current_node.parentNodeId is None:
            self.current_node = None
        else:
            self.current_node = self.tree_nodes_dict[self.current_node.parentNodeId]
        return self.current_node
