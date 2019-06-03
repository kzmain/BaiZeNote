from Tree.NoteTree import NoteTree


class Note:

    def __init__(self):
        self.note_tree = NoteTree()
        self.note_root = ""
        self.note_dict = ""

        self.current_parent_folder_relative_uri = ""
        self.current_target_sub_folder = ""

        # self.section_id = 0
        # self.notebook_dict = {}

    # def add_sections_notes(self, file_dir_dict):
    #     self.notebook_dict["section%s" % self.section_id] = file_dir_dict
    #     self.section_id += 1
