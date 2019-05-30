import json
import os

from Tree.NoteNode import NoteNode
from Tree.NoteRootNode import NoteRootNode


class NoteTree:
    current_node = None
    nodes_dict = {}
    node_id = 0

    def __init__(self):
        self.nodes_dict = {}
        self.current_node = None
        self.node_id = 0

    def add_child_node(self, node_uri):
        if self.current_node is None and len(self.nodes_dict) == 0:
            root_node = NoteRootNode()
            root_node.nodeId = self.node_id
            root_node.parentNodeId = None
            dir_json = (open("%s/%s/.dir_list.json" % (os.getcwd(), node_uri), "r")).read()
            file_json = (open("%s/%s/.file_list.json" % (os.getcwd(), node_uri), "r")).read()
            notebook_json = (open("%s/%s/.notebook.json" % (os.getcwd(), node_uri), "r")).read()
            root_node.dir_dict = json.loads(dir_json)
            root_node.file_dict = json.loads(file_json)
            root_node.note_dict = json.loads(notebook_json)
            node = root_node
        elif self.current_node is None and len(self.nodes_dict) > 0:
            raise Exception
        else:
            node = NoteNode()
            node.nodeId = self.node_id
            node.parentNodeId = self.current_node.nodeId
            self.current_node.childNodesIds.append(node.nodeId)
            dir_json = (open("%s/%s/.dir_list.json" % (os.getcwd(), node_uri), "r")).read()
            file_json = (open("%s/%s/.file_list.json" % (os.getcwd(), node_uri), "r")).read()
            node.dir_dict = json.loads(dir_json)
            node.file_dict = json.loads(file_json)
        self.nodes_dict[self.node_id] = node
        self.node_id += 1
        return

    def go_to_node(self, node_id):
        self.current_node = self.nodes_dict[node_id]
        return

    def go_to_parent_node(self):
        if self.current_node.parentNodeId is None:
            self.current_node = None
        else:
            self.current_node = self.nodes_dict[self.current_node.parentNodeId]
        return
