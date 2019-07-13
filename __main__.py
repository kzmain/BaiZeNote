import copy
import json
import logging
import os
import re
import sys

from Memory.Notebook import Notebook
from Processor.Constants.Paths import  Paths
from Processor.CoreProcessor import CoreProcessor as Core
from Processor.NotebookProcessor import NotebookProcessor
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


# ----------------------------------------------------------------------------------------------------------------------
# 如果 创建一相同的note，保存本地文件时需要 换名字
# 如果 创建一相同的section，保存本地文件时需要 换名字
# ----------------------------------------------------------------------------------------------------------------------


def main():
    # Check system configs, if a system config does not exist system will create default one
    # 检查系统的配置，如果系统配置不存系统将创建默认的配置
    Core.sys_configs_check()
    if "-g" in sys.argv:
        # 1. 获取需要转换的 所有 笔记本的路径,有新的写入系统，有失效的从系统删除
        notebooks_list = Core.sys_get_processing_notebooks_list()
        notebooks_list = Core.res_check_notebooks_validation(notebooks_list)
        # 1.1 空将要处理的列表，系统结束退出
        if len(notebooks_list) == 0:
            logging.critical("No notebook needs to process. Exit!")
            sys.exit(0)
        # 2. 获取转换后所有笔记的目标地
        notebooks_destination = Core.get_notebooks_destination()
        repository_html = "<meta charset=\"utf-8\">\n"
        # 3. 分别处理每个笔记本
        for notebook_path in notebooks_list:
            # 3.1 处理笔记本基础信息
            notebook = Notebook()
            notebook.notebook_root = notebook_path
            notebook.notebook_name = os.path.basename(notebook_path)
            notebook.notebook_dest = Core.get_notebook_destination(notebooks_destination, notebook.notebook_name)
            notebook.notebook_dict = Core.res_get_notebooks_info()[notebook_path]
            sections_dicts = Core.notebook_check_section_json(notebook.notebook_root)
            old_nodes_dict = notebook.notebook_tree.set_note_tree(notebook.notebook_root, sections_dicts)
            with open("/Users/kzmain/d.json", "w+") as a:
                a.write(json.dumps(sections_dicts))
            Paths.set_dest_path(notebook.notebook_dest, notebook.notebook_root)
            # 3.2 Prepare to html write
            repo_note_dict = copy.deepcopy(old_nodes_dict)
            nodes_dict = copy.deepcopy(old_nodes_dict)
            for key, node in nodes_dict.items():
                nodes_dict[key] = node.node_info_dict[NotebookProcessor.SECTION_DICT_NOTES_DICT]
            Core.prepare_file_writing()
            # 3.3 Start to write html file
            nodes_dict = Core.write_converted_htmls(notebook, nodes_dict)
            static_file_dict = Core.write_static_resources(notebook.statistic_files_dict)
            html_head = Core.generate_html_header(static_file_dict, nodes_dict)
            html_foot = Core.generate_html_footer(static_file_dict)
            if Mode.is_local_mode():
                html_body = Core.generate_html_body(html_foot, old_nodes_dict, nodes_dict)
                Core.local_mode_write_body_htmls(html_head, html_body)
                if Mode.is_r_local_mode():
                    repo_note_dict
                    repository_html += "<a href = \"%s%s%s\">%s</a>\n" % \
                                       ("./", notebook.notebook_name, "/index.html", notebook.notebook_name)
            elif Mode.is_server_mode():
                # nodes_dict = Core.write_converted_htmls(notebook, nodes_dict)
                # html_head = Core.write_static_resources(notebook, nodes_dict)
                with open(Paths.PATH_FULL_NOTEBOOK_DEST + "/source/section-menu.blade.html", "w+") as section_menu:
                    section_menu.write(old_nodes_dict[0].html_section_menu)
                if Mode.is_r_server_mode():
                    link_match = re.search(r"((?<=src=\")|(?<=href=\"))(?=\/source)", html_head)
                    while link_match:
                        start = html_head[:link_match.start()]
                        end = html_head[link_match.end():]
                        html_head = start + "/" + notebook.notebook_name + end

                        link_match = re.search(r"((?<=src=\")|(?<=href=\"))(?=\/source)", html_head)
                Core.server_mode_write_body_htmls(nodes_dict, html_head, html_foot)

                main_js_location = os.path.join(notebook.notebook_dest, "source/js/main.js")
                with open(main_js_location, "r+") as main_js:
                    js = main_js.read()
                with open(main_js_location, "w+") as main_js:
                    if Mode.is_r_server_mode():
                        main_js.write(("let prefix = \"/%s\";\n" % notebook.notebook_name) + js)
                    elif Mode.is_server_mode():
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
