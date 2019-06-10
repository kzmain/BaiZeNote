import copy
import os
from pathlib import Path

from HTML.HTML import HTML
from NotePath.Source import Source
from Tree.NoteNode import NoteNode
from Tree.NoteRootNode import NoteRootNode
from source.temp.svg.SVG import SVG


def test_note_dict(all_sections_info_dicts):
    all_sections_info_dicts["1"] = 1


class NoteTree:

    def __init__(self):
        self.next_node_id = 0
        self.current_node_id = -1
        self.modification_count = {}
        self.nodes_dict = {}
        self.node_id_root = None

    def add_child_node(self, node_info_dict):
        if len(self.nodes_dict) == 0:
            node = NoteRootNode()
            node.node_id_parent = None
            self.node_id_root = self.next_node_id
        elif len(self.nodes_dict) > 0:
            node = NoteNode()
            node.node_id_parent = self.current_node_id
            self.nodes_dict[self.current_node_id].node_id_children_list.append(self.next_node_id)
        else:
            raise Exception

        node.node_id = self.next_node_id
        node.node_name = node_info_dict[Source.SOURCE_SECTION_DICT_SECTION_NAME]
        node.node_info_dict = node_info_dict
        self.nodes_dict[node.node_id] = node
        self.next_node_id += 1
        return

    def go_to_node(self, node_id):
        if node_id < 0:
            raise IndexError
        self.current_node_id = node_id
        return

    def go_to_parent_node(self):
        if self.current_node_id < 0:
            raise IndexError
        if self.nodes_dict[self.current_node_id].parentNodeId is None:
            self.node_id_current = self.node_id_root
        else:
            self.node_id_current = self.nodes_dict[self.current_node_id].parentNodeId
        return

    def set_note_tree(self, notebook_root, notebook_section_path_rel, all_sections_info_dicts):
        section_info_not_need_list = [Source.SOURCE_SECTION_DICT_SECTION_MODIFICATION_TIME,
                                      Source.SOURCE_SECTION_DICT_SECTION_CREATION_TIME,
                                      Source.SOURCE_SECTION_DICT_REL_PATH]
        note_info_not_need_list = []
        section_path_rel = notebook_section_path_rel
        section_path_full = os.path.abspath(os.path.join(notebook_root, section_path_rel))

        current_node_info_dict = copy.deepcopy(all_sections_info_dicts[notebook_section_path_rel])
        current_node_notes_info_dict = current_node_info_dict[Source.SOURCE_SECTION_DICT_NOTES_DICT]

        for key in section_info_not_need_list:
            current_node_info_dict.pop(key)
        sub_nodes = list(current_node_info_dict.pop(Source.SOURCE_SECTION_DICT_SUB_SECTION_REL_PATH_DICT).values())

        current_node_id = self.next_node_id
        self.add_child_node(current_node_info_dict)

        for sub_nodes_path_rel in sub_nodes:
            self.go_to_node(current_node_id)
            self.set_note_tree(notebook_root, sub_nodes_path_rel, all_sections_info_dicts)
        self.generate_section_menu(current_node_id)
        return self.nodes_dict

    def generate_section_menu(self, section_id):
        # TODO WHEN SECTION STATUS: HIDE, LOCK WHAT TO DO
        if section_id < 0:
            raise IndexError
        section_node = copy.copy(self.nodes_dict[section_id])
        node_notes_count = len(section_node.node_info_dict[Source.SOURCE_SECTION_DICT_NOTES_DICT])
        if len(section_node.node_id_children_list) > 0:
            children_nodes_section_html = ""
            # 收集子section 的 section-menu
            # Gather sub-section's section menu
            for child_node_id in section_node.node_id_children_list:
                children_nodes_section_html += self.nodes_dict[child_node_id].html_section_menu
            # 当本 node 不为 root node 时，生成此 node 的 section menu
            # If current node is not root node, generate current node's section menu
            if str(type(section_node)) == str(type(NoteRootNode())):
                section_node.html_section_menu = \
                    HTML.sections_span % (
                        section_id, section_id, section_id, SVG.sections_svg,
                        section_node.node_name, section_id, children_nodes_section_html
                    )
            else:
                section_node.html_section_menu = children_nodes_section_html
        # 2. 没有 sub-section 但有笔记
        # 2. Has NO sub-section and has notes
        elif len(section_node.node_id_children_list) == 0 and node_notes_count > 0:
            section_node.html_section_menu = HTML.no_sections_span % \
                                (section_id, section_id, SVG.no_sections_svg, section_node.node_name)
        # 3. 没有 sub-section 没有笔记
        # 3. Has NO sub-section and has NO notes
        else:
            section_node.html_section_menu = \
                HTML.no_notes_no_sections_span % \
                (section_id, section_id, SVG.no_notes_no_sections_svg, section_node.node_name)

        self.nodes_dict[section_id] = section_node
        return
    # # 📕1. 核心任务
    # #   1.1. 处理当前 node 的section menu
    # #       当前 node 的section menu 应该包含其子node的section menu
    # # 📗2. Section menu 类型
    # #   2.1 有 sub-section （不管其是否有笔记）
    # #   2.2 没有 sub-section 但有笔记
    # #   2.3 没有 sub-section 没有笔记
    # # ----------------------------------------------------------------------------------------------------------------------
    # # 📕1. Core Tasks
    # #   1.1. Process current node's section menu
    # #       current node's section menu need also contains it's sub-nodes' section
    # # 📗2.Section menu has three types:
    # #   2.1. Has sub-section (no matter if has notes)
    # #   2.2. Has NO sub-section and has notes
    # #   2.3. Has NO sub-section and has NO notes
    # @staticmethod
    # def process_section_menu(note_tree):
    #     current_node = note_tree.current_node
    #     # 1. 有 sub-section （不管其是否有笔记）
    #     # 1. Has sub-section (no matter if has notes)
    #     if len(current_node.section_dict) > 0:
    #         current_node_child_nodes_list = current_node.childNodesIds.copy()
    #         child_nodes_html = ""
    #         # 收集子section 的 section-menu
    #         # Gather sub-section's section menu
    #         for node_id in current_node_child_nodes_list:
    #             child_nodes_html += note_tree.tree_nodes_dict[node_id].html
    #         # 当本 node 不为 root node 时，生成此 node 的 section menu
    #         # If current node is not root node, generate current node's section menu
    #         if current_node.name != "Index":
    #             current_node.html = \
    #                 HTML.sections_span % (
    #                     current_node.nodeId, current_node.nodeId, current_node.nodeId, SVG.sections_svg,
    #                     current_node.name, current_node.nodeId, child_nodes_html
    #                 )
    #         else:
    #             current_node.html = child_nodes_html
    #     # 2. 没有 sub-section 但有笔记
    #     # 2. Has NO sub-section and has notes
    #     elif len(current_node.section_dict) == 0 and len(current_node.md_dict) > 0:
    #         current_node.html = HTML.no_sections_span % \
    #                             (current_node.nodeId, current_node.nodeId, SVG.no_sections_svg, current_node.name)
    #     # 3. 没有 sub-section 没有笔记
    #     # 3. Has NO sub-section and has NO notes
    #     else:
    #         current_node.html = \
    #             HTML.no_notes_no_sections_span % \
    #             (current_node.nodeId, current_node.nodeId, SVG.no_notes_no_sections_svg, current_node.name)
    #     note_tree.current_node = current_node
    #     return note_tree

    # # 📕1. 核心任务：
    # #   1.1. 处理当前node信息，并将其添加进node_tree（储存note的相关信息）
    # #   1.1.1 将当前 node 所有子的 note（md文件）为 html 文件
    # #   1.2. 处理子node信息，并将其添加为当前node的子node（储存note的相关信息）
    # #   1.3. 生成当前 node 的 section menu
    # # 📗2. 相关信息
    # #   2.1 文件夹 - Section - Node 的对应关系
    # #       硬盘中"文件夹" -> HTML笔记中的Section -> 内存中 Node
    # #   2.2 .md文件 - 笔记 （Note） 的对应关系
    # #       硬盘中".md文件" -> HTML笔记中的 笔记（Note）
    # # 📘3. 相关functions
    # #   3.1. get_section_info_dict()
    # #   3.2. process_section_menu()
    # # ----------------------------------------------------------------------------------------------------------------------
    # # 📕1. Core Tasks:
    # #   1.1. Process current node's info, and add it into node_tree, which stores all note related info
    # #   1.1.1 Generate all current node's notes' (md files) md files
    # #   1.2. Process current node's sub-nodes' info, and add them into node tree, which stores all note related info
    # #   1.3. Generate current node's section menu
    # # 📗2. Related info
    # #   2.1 Folder - section - node 's relationship
    # #       "Folder" in hard disk -> section in HTML file -> node in RAM
    # #   2.2 .md files - note 的对应关系
    # #       ".md file" in hard disk-> note in HTML file
    # # 📘3. Related functions
    # #   3.1. get_section_info_dict()
    # #   3.2. process_section_menu()
    # def initial_files_and_sections(self, note_root, section_path_relative):
    #     # 1. 获取 目标文件夹的相对文件位置
    #     # 1. Get target folder relative path
    #     # if target_sub_section != "":
    #     #     target_section_path_relative = "%s%s/" % (parent_path_relative, target_sub_section)
    #     # else:
    #     #     target_section_path_relative = parent_path_relative
    #     target_section_path_abs = os.path.abspath(os.path.join(note_root, section_path_relative))
    #
    #     # 3. 在 note_tree 中将现在的node添加为子node
    #     # 3. Add current node in to note_tree
    #     node_name = os.path.basename(target_section_path_abs)
    #     note.note_tree.add_child_node(node_name, section_info_dict)
    #     # 4. 处理当前node所有的子node
    #     #   - 因为他本身的section menu基于他的所有子node的情况，只有所有子node的section menu确定了才能完成其section menu
    #     # Process current node's children's nodes
    #     #   - This because a section's menu is based on it's children's nodes circumstance, only all its children nodes'
    #     # section menu is generated, can confirm current node's section menu
    #     current_node_id = note.note_tree.node_id - 1
    #     current_node = note.note_tree.go_to_node(current_node_id)
    #     dir_list = []
    #     # 4.1 获取所有的 子文件夹/子section
    #     # 4.1 Get all sub-folders/sub-sections
    #     for key, value in current_node.section_dict.items():
    #         dir_list.append(value["section_name"])
    #     # 4.2 处理子section的核心
    #     # 4.2 Core part of processing sub-sections
    #     while len(dir_list) > 0:
    #         note.note_tree.go_to_node(current_node_id)
    #         new_target_sub_folder = dir_list.pop()
    #         new_target_section_path_relative = os.path.join(section_path_relative, new_target_sub_folder)
    #         note = initial_files_and_sections(note, new_target_section_path_relative)
    #         note.note_tree.go_to_parent_node()
    #     # 5. 处理当前 node 的 section menu
    #     # 5. Generate current node's section menu
    #     note.note_tree = process_section_menu(note.note_tree)
    #     return note


note_book_root_test = "/Users/kzmain/_Repository/📚Head_First_Data_Analysis_2009"
all_sections_info_dicts_test = {
    '.': {'REL_PATH': '.', 'SECTION_NAME': '📚Head_First_Data_Analysis_2009', 'SECTION_LOCK': False,
          'SECTION_HIDE': False, 'SECTION_TAG': [], 'SECTION_CREATION_TIME': 'Mon Jun 10 06:25:33 2019',
          'SECTION_MODIFICATION_TIME': ['Wed May 29 19:22:12 2019'],
          'SUB_SECTION_REL_PATH_DICT': {'0': 'Intro', '1': '1.Data Analysis procedure', '2': '.idea'},
          'NOTES_DICT': {}},
    'Intro': {'REL_PATH': 'Intro', 'SECTION_NAME': 'Intro', 'SECTION_LOCK': False, 'SECTION_HIDE': False,
              'SECTION_TAG': [], 'SECTION_CREATION_TIME': 'Mon Jun 10 06:41:42 2019',
              'SECTION_MODIFICATION_TIME': ['Mon Jun 10 06:41:42 2019'],
              'SUB_SECTION_REL_PATH_DICT': {'0': 'Intro/untitled folder'}, 'NOTES_DICT': {
            '0': {'NOTE_FILE_NAME': 'Intro', 'NOTE_FILE_PATH': 'Intro/Intro.md', 'NOTE_FILE_TYPE': '.md',
                  'NOTE_REFERENCES': {}, 'NOTE_LOCK': False, 'NOTE_HIDE': False, 'NOTE_TAG': [],
                  'NOTE_CREATION_TIME': 'Mon Jun 10 06:33:36 2019',
                  'NOTE_MODIFICATION_TIME': ['Mon Jun 10 06:33:36 2019']}}},
    'Intro/untitled folder': {'REL_PATH': 'Intro/untitled folder', 'SECTION_NAME': 'untitled folder',
                              'SECTION_LOCK': False, 'SECTION_HIDE': False, 'SECTION_TAG': [],
                              'SECTION_CREATION_TIME': 'Mon Jun 10 19:54:08 2019',
                              'SECTION_MODIFICATION_TIME': ['Mon Jun 10 19:54:08 2019'],
                              'SUB_SECTION_REL_PATH_DICT': {'0': 'Intro/untitled folder/untitled folder'},
                              'NOTES_DICT': {}},
    'Intro/untitled folder/untitled folder': {'REL_PATH': 'Intro/untitled folder/untitled folder',
                                              'SECTION_NAME': 'untitled folder', 'SECTION_LOCK': False,
                                              'SECTION_HIDE': False, 'SECTION_TAG': [],
                                              'SECTION_CREATION_TIME': 'Mon Jun 10 19:54:08 2019',
                                              'SECTION_MODIFICATION_TIME': ['Mon Jun 10 19:54:08 2019'],
                                              'SUB_SECTION_REL_PATH_DICT': {}, 'NOTES_DICT': {}},
    '1.Data Analysis procedure': {'REL_PATH': '1.Data Analysis procedure', 'SECTION_NAME': '1.Data Analysis procedure',
                                  'SECTION_LOCK': False, 'SECTION_HIDE': False, 'SECTION_TAG': [],
                                  'SECTION_CREATION_TIME': 'Mon Jun 10 06:25:33 2019',
                                  'SECTION_MODIFICATION_TIME': ['Sat Jun  1 00:30:37 2019'],
                                  'SUB_SECTION_REL_PATH_DICT': {'0': '1.Data Analysis procedure/1. Define the problem',
                                                                '1': '1.Data Analysis procedure/2. Disassemble',
                                                                '2': '1.Data Analysis procedure/3. Evaluate',
                                                                '3': '1.Data Analysis procedure/4. Decide'},
                                  'NOTES_DICT': {
                                      '0': {'NOTE_FILE_NAME': 'Data Analysis procedure',
                                            'NOTE_FILE_PATH': '1.Data Analysis procedure/Data Analysis procedure.md',
                                            'NOTE_FILE_TYPE': '.md',
                                            'NOTE_REFERENCES': {}, 'NOTE_LOCK': False, 'NOTE_HIDE': False,
                                            'NOTE_TAG': [],
                                            'NOTE_CREATION_TIME': 'Mon Jun 10 06:25:33 2019',
                                            'NOTE_MODIFICATION_TIME': ['Mon Jun 10 06:25:33 2019']},
                                      '2': {'NOTE_FILE_NAME': 'Sharpen_Your_Pencil_P47',
                                            'NOTE_FILE_PATH': '1.Data Analysis procedure/Sharpen_Your_Pencil_P47.md',
                                            'NOTE_FILE_TYPE': '.md',
                                            'NOTE_REFERENCES': {}, 'NOTE_LOCK': False, 'NOTE_HIDE': False,
                                            'NOTE_TAG': [],
                                            'NOTE_CREATION_TIME': 'Mon Jun 10 06:25:33 2019',
                                            'NOTE_MODIFICATION_TIME': ['Mon Jun 10 06:25:33 2019',
                                                                       'Mon Jun 10 19:38:57 2019']},
                                      '3': {'NOTE_FILE_NAME': 'Sharpen_Your_Pencil_P52',
                                            'NOTE_FILE_PATH': '1.Data Analysis procedure/Sharpen_Your_Pencil_P52.md',
                                            'NOTE_FILE_TYPE': '.md',
                                            'NOTE_REFERENCES': {}, 'NOTE_LOCK': False, 'NOTE_HIDE': False,
                                            'NOTE_TAG': [],
                                            'NOTE_CREATION_TIME': 'Mon Jun 10 06:25:33 2019',
                                            'NOTE_MODIFICATION_TIME': ['Mon Jun 10 06:25:33 2019']},
                                      '5': {'NOTE_FILE_NAME': 'Sharpen_Your_Pencil_P47 copy',
                                            'NOTE_FILE_PATH': '1.Data Analysis procedure/Sharpen_Your_Pencil_P47 copy.md',
                                            'NOTE_FILE_TYPE': '.md', 'NOTE_REFERENCES': {}, 'NOTE_LOCK': False,
                                            'NOTE_HIDE': False,
                                            'NOTE_TAG': [], 'NOTE_CREATION_TIME': 'Mon Jun 10 06:43:55 2019',
                                            'NOTE_MODIFICATION_TIME': ['Mon Jun 10 06:43:55 2019',
                                                                       'Mon Jun 10 19:38:51 2019']}}},
    '1.Data Analysis procedure/1. Define the problem': {'REL_PATH': '1.Data Analysis procedure/1. Define the problem',
                                                        'SECTION_NAME': '1. Define the problem', 'SECTION_LOCK': False,
                                                        'SECTION_HIDE': False, 'SECTION_TAG': [],
                                                        'SECTION_CREATION_TIME': 'Mon Jun 10 06:25:33 2019',
                                                        'SECTION_MODIFICATION_TIME': ['Sat Jun  1 00:30:37 2019'],
                                                        'SUB_SECTION_REL_PATH_DICT': {}, 'NOTES_DICT': {
            '0': {'NOTE_FILE_NAME': '1',
                  'NOTE_FILE_PATH': '1.Data Analysis procedure/1. Define the problem/1. Define the problem.md',
                  'NOTE_FILE_TYPE': '.md', 'NOTE_REFERENCES': {}, 'NOTE_LOCK': False, 'NOTE_HIDE': False,
                  'NOTE_TAG': [], 'NOTE_CREATION_TIME': 'Mon Jun 10 06:25:33 2019',
                  'NOTE_MODIFICATION_TIME': ['Mon Jun 10 06:25:33 2019']}}},
    '1.Data Analysis procedure/2. Disassemble': {'REL_PATH': '1.Data Analysis procedure/2. Disassemble',
                                                 'SECTION_NAME': '2. Disassemble', 'SECTION_LOCK': False,
                                                 'SECTION_HIDE': False, 'SECTION_TAG': [],
                                                 'SECTION_CREATION_TIME': 'Mon Jun 10 06:25:33 2019',
                                                 'SECTION_MODIFICATION_TIME': ['Sat Jun  1 00:30:37 2019'],
                                                 'SUB_SECTION_REL_PATH_DICT': {}, 'NOTES_DICT': {
            '0': {'NOTE_FILE_NAME': '2', 'NOTE_FILE_PATH': '1.Data Analysis procedure/2. Disassemble/2. Disassemble.md',
                  'NOTE_FILE_TYPE': '.md', 'NOTE_REFERENCES': {}, 'NOTE_LOCK': False, 'NOTE_HIDE': False,
                  'NOTE_TAG': [], 'NOTE_CREATION_TIME': 'Mon Jun 10 06:25:33 2019',
                  'NOTE_MODIFICATION_TIME': ['Mon Jun 10 06:25:33 2019']}}},
    '1.Data Analysis procedure/3. Evaluate': {'REL_PATH': '1.Data Analysis procedure/3. Evaluate',
                                              'SECTION_NAME': '3. Evaluate', 'SECTION_LOCK': False,
                                              'SECTION_HIDE': False, 'SECTION_TAG': [],
                                              'SECTION_CREATION_TIME': 'Mon Jun 10 06:25:33 2019',
                                              'SECTION_MODIFICATION_TIME': ['Sat Jun  1 00:30:37 2019'],
                                              'SUB_SECTION_REL_PATH_DICT': {}, 'NOTES_DICT': {
            '0': {'NOTE_FILE_NAME': '3', 'NOTE_FILE_PATH': '1.Data Analysis procedure/3. Evaluate/3. Evaluate.md',
                  'NOTE_FILE_TYPE': '.md', 'NOTE_REFERENCES': {}, 'NOTE_LOCK': False, 'NOTE_HIDE': False,
                  'NOTE_TAG': [], 'NOTE_CREATION_TIME': 'Mon Jun 10 06:25:33 2019',
                  'NOTE_MODIFICATION_TIME': ['Mon Jun 10 06:25:33 2019']}}},
    '1.Data Analysis procedure/4. Decide': {'REL_PATH': '1.Data Analysis procedure/4. Decide',
                                            'SECTION_NAME': '4. Decide', 'SECTION_LOCK': False, 'SECTION_HIDE': False,
                                            'SECTION_TAG': [], 'SECTION_CREATION_TIME': 'Mon Jun 10 06:25:33 2019',
                                            'SECTION_MODIFICATION_TIME': ['Sat Jun  1 00:30:37 2019'],
                                            'SUB_SECTION_REL_PATH_DICT': {}, 'NOTES_DICT': {
            '0': {'NOTE_FILE_NAME': '4', 'NOTE_FILE_PATH': '1.Data Analysis procedure/4. Decide/4. Decide.md',
                  'NOTE_FILE_TYPE': '.md', 'NOTE_REFERENCES': {}, 'NOTE_LOCK': False, 'NOTE_HIDE': False,
                  'NOTE_TAG': [], 'NOTE_CREATION_TIME': 'Mon Jun 10 06:25:33 2019',
                  'NOTE_MODIFICATION_TIME': ['Mon Jun 10 06:25:33 2019']}}},
    '.idea': {'REL_PATH': '.idea', 'SECTION_NAME': '.idea', 'SECTION_LOCK': False, 'SECTION_HIDE': False,
              'SECTION_TAG': [], 'SECTION_CREATION_TIME': 'Mon Jun 10 06:42:18 2019',
              'SECTION_MODIFICATION_TIME': ['Mon Jun 10 06:42:18 2019'], 'SUB_SECTION_REL_PATH_DICT': {},
              'NOTES_DICT': {}}}
note_tree_test = NoteTree()
a = note_tree_test.set_note_tree(note_book_root_test, ".", all_sections_info_dicts_test)
print()
