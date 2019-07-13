import copy

from Memory.Tree.NoteNode import NoteNode
from Memory.Tree.NoteRootNode import NoteRootNode
from Processor.Constants import HTML
from Processor.NotebookProcessor import NotebookProcessor
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

    # Add a child node to current or root node
    # 加一个子node到当前node或者加入到根node
    # @For
    # NoteTree.__set_note_tree
    def __add_child_node(self, node_info_dict):
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
        node.node_name = node_info_dict[NotebookProcessor.SECTION_DICT_SECTION_NAME]
        node.node_info_dict = node_info_dict
        self.nodes_dict[node.node_id] = node
        self.next_node_id += 1

    # Go to specific node
    # 去特定的node
    # @For
    # NoteTree.__set_note_tree
    def __go_to_node(self, node_id):
        if node_id < 0:
            raise IndexError
        self.current_node_id = node_id

    # Setup note tree of a notebook
    # 为系统建立笔记本树
    # @Input:
    # notebook_root: Notebook's root location (resource repository location)
    # sections_dicts: Notebook sections' dict
    # notebook_root: 笔记本的根目录（即笔记本的源仓库所在位置）
    # sections_dicts: 笔记本section字典
    # @Return:
    # tree_dict: Notebook's tree nodes' dictionary
    # tree_dict: 笔记本树的节点字典
    def set_note_tree(self, notebook_root, sections_dicts):
        tree_dict = self.__set_note_tree(notebook_root, ".", sections_dicts)
        return tree_dict

    # Setup note tree from an entry point
    # 从给定的进入点建立笔记本树
    # @Input:
    # notebook_root: Notebook's root location (resource repository location)
    # section_path_rel: Section's relative path
    # sections_dicts: Notebook sections' dict
    # notebook_root: 笔记本的根目录（即笔记本的源仓库所在位置）
    # section_path_rel: 笔记本section的相对路径
    # sections_dicts: 笔记本section字典
    # @Return
    # Notebook tree of a specific entry point
    # 指定切入点的笔记本树
    # @For
    # NoteTree.set_note_tree
    def __set_note_tree(self, notebook_root, section_path_rel, sections_dicts):
        needless_info = [NotebookProcessor.SECTION_DICT_SECTION_UPDATE_TIME,
                         NotebookProcessor.SECTION_DICT_SECTION_CREATION_TIME,
                         NotebookProcessor.SECTION_DICT_REL_PATH]

        cur_node_dict = copy.deepcopy(sections_dicts[section_path_rel])
        # 1. 移除不需要的信息
        for key in needless_info:
            cur_node_dict.pop(key)
        sub_nodes = list(cur_node_dict.pop(NotebookProcessor.SECTION_DICT_SUB_SECTION_REL_PATH_DICT).values())
        # 2. 添加节点
        # 3. 如果有子节点处理子节点
        current_node_id = self.next_node_id
        self.__add_child_node(cur_node_dict)
        for sub_nodes_path_rel in sub_nodes:
            self.__go_to_node(current_node_id)
            self.__set_note_tree(notebook_root, sub_nodes_path_rel, sections_dicts)
        # 4. 处理当前节点的section menu
        self.__generate_html_section_menu(current_node_id)
        return self.nodes_dict

    # Generate html section menu of current section
    # 给指定section生存section菜单
    # @Input:
    # section_id: Target section id
    # section_id: 目标section id
    # @For
    # NoteTree.set_note_tree
    def __generate_html_section_menu(self, section_id):
        # TODO WHEN SECTION STATUS: HIDE, LOCK WHAT TO DO
        if section_id < 0:
            raise IndexError
        section_node = copy.copy(self.nodes_dict[section_id])
        notes_count = len(section_node.node_info_dict[NotebookProcessor.SECTION_DICT_NOTES_DICT])
        # 1.1 有子section
        if len(section_node.node_id_children_list) > 0:
            children_nodes_section_html = ""
            # 收集子section 的 section-menu
            # Gather sub-section's section menu
            for child_node_id in section_node.node_id_children_list:
                children_nodes_section_html += self.nodes_dict[child_node_id].html_section_menu
            # 当本 node 不为 root node 时，生成此 node 的 section menu
            # If current node is not root node, generate current node's section menu
            if str(type(section_node)) != str(type(NoteRootNode())):
                section_node.html_section_menu = \
                    HTML.sections_span % (
                        section_id, section_id, section_id, SVG.sections_svg,
                        section_node.node_name, section_id, children_nodes_section_html
                    )
            # 如果有子文件夹就一定会到这里，但是这个是quick note区域， 无子section, 需要检查是否有note
            else:
                svg = SVG.no_sections_svg if notes_count > 0 else SVG.no_notes_no_sections_svg
                section_node.html_section_menu = HTML.root_sections_span % (
                    section_id, section_id, svg,
                    section_node.node_name, children_nodes_section_html
                )
        # 1.2. 没有 sub-section 但有笔记
        # 1.2. Has NO sub-section and has notes
        elif len(section_node.node_id_children_list) == 0 and notes_count > 0:
            section_node.html_section_menu = HTML.no_sections_span % \
                                             (section_id, section_id, SVG.no_sections_svg, section_node.node_name)
        # 1.3. 没有 sub-section 没有笔记
        # 1.3. Has NO sub-section and has NO notes
        else:
            section_node.html_section_menu = \
                HTML.no_notes_no_sections_span % \
                (section_id, section_id, SVG.no_notes_no_sections_svg, section_node.node_name)

        self.nodes_dict[section_id] = section_node
