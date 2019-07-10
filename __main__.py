import copy
import os
import re
import shutil
import sys
import time
import logging
import json
from pathlib import Path

from Memory.Notebook import Notebook
from Processor.Constants import Paths, Constants
from Processor.NotebookProcessor import NotebookProcessor
from Processor.CoreProcessor import Processor
from Tools.File import File
from source.temp.svg.SVG import SVG
import emarkdown.markdown as md

from Tools import URI


# ----------------------------------------------------------------------------------------------------------------------
# 如果 创建一相同的note，保存本地文件时需要 换名字
# 如果 创建一相同的section，保存本地文件时需要 换名字
# ----------------------------------------------------------------------------------------------------------------------


# 📕Note book 参数信息
# "-n" 模式 创建新的notebook
# "-g" 模式 转换Markdown文件成静态html网页文件，"-g" 模式有两个子模式 "-server" 和 "-local"
#     "-local" 模式仅生成一个 "index.html"，用于在本地查看
#     "-server" 模式每个页面都生成单独的静态网页文件，以便在线用于在线网站
# ----------------------------------------------------------------------------------------------------------------------
# 📕Note book argument info
# "-n" mode - Create a new note book
# "-g" mode - Generate Markdown files to static html files, "-g" mode has two sub-mode "-server" and "-local"
#     "-local" mode will generate one "index.html", for easy local use
#     "-server" mode will generate a corresponding web page for each md files, for online website
def main():
    # note = Notebook()
    # ！！！！ 这是个initial 需分拆
    Processor.sys_configs_check()

    if "-g" in sys.argv:
        # 1. 获取需要转换的 所有 笔记本的路径,有新的写入系统，有失效的从系统删除
        notebooks_list = Processor.sys_get_processing_notebooks_list()
        notebooks_list = Processor.res_check_notebooks_validation(notebooks_list)
        if len(notebooks_list) == 0:
            logging.error("No notebook needs to process. Exit!")
            return
        # 2. 获取转换后所有笔记的目标地
        notebooks_destination = Processor.get_notebooks_destination()
        for notebook_path in notebooks_list:
            # 2. 获取转换后 当前笔记的目标地
            notebook = Notebook()
            notebook.notebook_root = notebook_path
            notebook.notebook_name = os.path.basename(notebook_path)
            notebook.notebook_dest = Processor.get_notebook_destination(notebooks_destination, notebook.notebook_name)
            notebook.notebook_dict = Processor.res_get_notebooks_info()[notebook_path]
            sections_info_dicts = Processor.notebook_check_section_json(notebook.notebook_root)
            nodes_dict = notebook.notebook_tree.set_note_tree(notebook.notebook_root, ".", sections_info_dicts)
            nodes_dict = copy.deepcopy(nodes_dict)

            Processor.prepare_file_writing(notebook.notebook_root, notebook.notebook_dest)

            if Constants.STANDARD_LOCAL_MODE in sys.argv:
                for key, node in nodes_dict.items():
                    nodes_dict[key] = node.node_info_dict[NotebookProcessor.SECTION_DICT_NOTES_DICT]
                nodes_dict = Processor.local_write_converted_htmls(notebook, nodes_dict)
                html_head = Processor.server_mode_write_static_resources(notebook, nodes_dict)
                Processor.local_mode_write_body_htmls(notebook, html_head)
            elif Constants.STANDARD_SERVER_MODE in sys.argv:
                # 处理 node dict
                nodes_dict = copy.deepcopy(nodes_dict)
                for key, node in nodes_dict.items():
                    nodes_dict[key] = node.node_info_dict[NotebookProcessor.SECTION_DICT_NOTES_DICT]
                nodes_dict = Processor.server_write_converted_htmls(notebook, nodes_dict)
                html_head = Processor.server_mode_write_static_resources(notebook, nodes_dict)
                Processor.server_mode_write_body_htmls(notebook, nodes_dict, html_head)
    else:
        raise Exception


if __name__ == '__main__':
    main()
