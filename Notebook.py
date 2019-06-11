from Tree.NoteTree import NoteTree


class Notebook:

    def __init__(self):
        self.notebook_tree = NoteTree()
        self.notebook_root = ""
        self.notebook_dict = ""
        self.notebook_name = ""
        self.notebook_dest = ""
        self.modified_time = ""
        self.statistic_files_dict = {}

        self.current_parent_folder_relative_uri = ""
        self.current_target_sub_folder = ""







