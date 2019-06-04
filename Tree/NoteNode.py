class NoteNode:
    nodeId = None
    parentNodeId = None
    childNodesIds = []
    md_dict = {}
    section_dict = {}
    name = "Index"
    html = ""
    relative_path = ""

    def __init__(self):
        self.nodeId = None
        self.parentNodeId = None
        self.childNodesIds = []
        self.md_dict = {}
        self.section_dict = {}
        self.name = "Index"
        self.html = ""
        self.relative_path = ""

