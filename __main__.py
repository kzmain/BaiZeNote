import copy
import logging
import os
import re
import sys

from Memory.Notebook import Notebook
from Processor.Constants import Constants
from Processor.CoreProcessor import Processor
from Processor.NotebookProcessor import NotebookProcessor

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
from Tools import Mode


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
        repository_html = "<meta charset=\"utf-8\">\n"
        for notebook_path in notebooks_list:
            # 2. 获取转换后 当前笔记的目标地
            notebook = Notebook()
            notebook.notebook_root = notebook_path
            notebook.notebook_name = os.path.basename(notebook_path)
            notebook.notebook_dest = Processor.get_notebook_destination(notebooks_destination, notebook.notebook_name)
            notebook.notebook_dict = Processor.res_get_notebooks_info()[notebook_path]
            sections_info_dicts = Processor.notebook_check_section_json(notebook.notebook_root)
            nodes_dict = notebook.notebook_tree.set_note_tree(notebook.notebook_root, ".", sections_info_dicts)
            repo_note_dict = copy.deepcopy(nodes_dict)
            nodes_dict = copy.deepcopy(nodes_dict)

            Processor.prepare_file_writing(notebook.notebook_root, notebook.notebook_dest)
            if Mode.is_local_mode():
                for key, node in nodes_dict.items():
                    nodes_dict[key] = node.node_info_dict[NotebookProcessor.SECTION_DICT_NOTES_DICT]
                nodes_dict = Processor.local_write_converted_htmls(notebook, nodes_dict)
                html_head = Processor.server_mode_write_static_resources(notebook, nodes_dict)
                Processor.local_mode_write_body_htmls(notebook, html_head)
                if Mode.is_r_local_mode():
                    repo_note_dict
                    repository_html += "<a href = \"%s%s%s\">%s</a>\n" % \
                                       ("./", notebook.notebook_name, "/index.html", notebook.notebook_name)
            elif Mode.is_server_mode():
                # 处理 node dict
                nodes_dict = copy.deepcopy(nodes_dict)
                for key, node in nodes_dict.items():
                    nodes_dict[key] = node.node_info_dict[NotebookProcessor.SECTION_DICT_NOTES_DICT]
                nodes_dict = Processor.server_write_converted_htmls(notebook, nodes_dict)
                html_head = Processor.server_mode_write_static_resources(notebook, nodes_dict)
                if Mode.is_r_server_mode():
                    link_match = re.search(r"((?<=src=\")|(?<=href=\"))(?=\/source)", html_head)
                    while link_match:
                        start = html_head[:link_match.start()]
                        end = html_head[link_match.end():]
                        html_head = start + "/" + notebook.notebook_name + end

                        link_match = re.search(r"((?<=src=\")|(?<=href=\"))(?=\/source)", html_head)
                Processor.server_mode_write_body_htmls(notebook, nodes_dict, html_head)

                main_js_location = os.path.join(notebook.notebook_dest, "source/js/main.js")
                with open(main_js_location, "r+") as main_js:
                    js = main_js.read()
                with open(main_js_location, "w+") as main_js:
                    if Mode.is_r_server_mode():
                        main_js.write(("let prefix = \"/%s\";\n" % notebook.notebook_name) + js)
                    elif Mode.is_local_mode():
                        main_js.write("let prefix = \"\";\n" + js)
                    else:
                        raise Exception
                if Mode.is_r_server_mode():
                    repo_note_dict
                    repository_html += "<a href = \"%s%s%s\">%s</a>\n" % \
                                       ("/", notebook.notebook_name, "/Intro.html", notebook.notebook_name)
            else:
                raise Exception

        if Mode.is_r_local_mode():
            local_note_books_dest = notebooks_destination + "/local"
            with open(os.path.join(local_note_books_dest, "index.html"), "w+") as repository_file:
                repository_file.write(repository_html)
        elif Mode.is_r_server_mode():
            local_note_books_dest = notebooks_destination + "/server"
            with open(os.path.join(local_note_books_dest, "index.html"), "w+") as repository_file:
                repository_file.write(repository_html)

    else:
        raise Exception


if __name__ == '__main__':
    main()
