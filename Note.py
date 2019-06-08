from Tree.NoteTree import NoteTree


class Note:

    def __init__(self):
        self.note_tree = NoteTree()
        self.note_root = ""
        self.note_dict = ""
        self.note_name = ""

        self.current_parent_folder_relative_uri = ""
        self.current_target_sub_folder = ""
