class NoteNode:
    nodeId = None
    parentNodeId = None
    childNodesIds = []
    dir_dict = {}
    file_dict = {}
    name = "Index"
    html = ""

    def __init__(self):
        self.nodeId = None
        self.parentNodeId = None
        self.childNodesIds = []
        self.dir_dict = {}
        self.x = {}
        self.name = "Index"
        self.html = ""

