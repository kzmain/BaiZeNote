import copy
import logging
import os
import re
import shutil
import sys

from Memory.Notebook import Notebook
from Constants.Paths import Paths
from Processor.CoreProcessor import CoreProcessor as Core
from Processor.NotebookProcessor import NotebookProcessor
from Tools import Mode


# 📕Note book 参数信息
# "-g" 模式 转换Markdown文件成静态html网页文件，"-g" 模式有四个子模式
#     "-local" 模式每个笔记本仅生成一个 "index.html"，用于在本地查看
#     "-rlocal" 除了"-local"模式的文件外，为所有选中的笔记本生成 一个 主页面方便于查看
#     "-server" 模式每个页面都生成单独的静态网页文件，以便在线用于在线网站
#     "-rserver" 除了"-server"模式的文件外，为所有选中的笔记本生成 一个 主页面方便于查看
# ----------------------------------------------------------------------------------------------------------------------
# 📕Note book argv info
# "-g" mode - Generate Markdown files to static html files, "-g" mode has four sub-modes
#     "-local" mode will generate one "index.html" for each notebook, for easy local use
#     "-rlocal" besides files in "-local" mode, generate AN index page to display all notebooks
#     "-server" mode will generate a corresponding web page for each note files, for online website usage
#     "-rserver" besides files in "-server" mode, generate AN index page to display all notebooks

def main():
    # 0. 检查系统的配置，如果系统配置不存系统将创建默认的配置
    # ------------------------------------------------------------------------------------------------------------------
    # 0. Check system configs, if a system config does not exist system will create default one
    Core.sys_configs_check()
    if "-g" in sys.argv:
        if not (Mode.is_server_mode() or Mode.is_local_mode()):
            logging.error("Please enter correct mode")
            raise Exception
        # 1. 获取需要转换的 所有 笔记本的路径，
        #   如果笔记本路径不在系统配置中则储存，
        #   如果笔记本路径失效的从系统配置中删除。
        # --------------------------------------------------------------------------------------------------------------
        # 1. Get all required processing notebooks' paths，
        #   if a notebook's path not in system config, store it in system config，
        #   if a notebook's path not valid any longer, remove it from system config。
        notebooks_list = Core.sys_get_processing_notebooks_list()
        notebooks_list = Core.res_check_notebooks_validation(notebooks_list)
        # 1.1 空将要处理的列表，系统结束退出！
        # --------------------------------------------------------------------------------------------------------------
        # 1.1 If processing notebook list is empty, exit!
        if len(notebooks_list) == 0:
            logging.critical("No notebook needs to process. Exit!")
            sys.exit(0)
        # 2. 获取转换后所有笔记的目标地
        # --------------------------------------------------------------------------------------------------------------
        # 2. Get all notebooks' destination
        notebooks_destination = Core.get_notebooks_destination()
        repository_html = "<meta charset=\"utf-8\">\n"
        # 3. 分别处理每个笔记本
        # --------------------------------------------------------------------------------------------------------------
        # 3. Start to processing each notebook
        notebook_name_list = []
        for notebook_path in notebooks_list:
            # 3.1 处理笔记本基础信息
            # ----------------------------------------------------------------------------------------------------------
            # 3.1 Processing notebook basic info
            notebook = Notebook()
            notebook.notebook_root = notebook_path
            notebook.notebook_dict = Core.res_get_notebooks_info()[notebook_path]
            notebook.notebook_name = Core.res_get_notebooks_info()[notebook_path]["NOTEBOOK_NAME"]
            while notebook.notebook_name in notebook_name_list:
                notebook_name_counter = 0
                while (notebook.notebook_name + "_" + str(notebook_name_counter)) in notebook_name_list:
                    notebook_name_counter += 1
                notebook.notebook_name += "_" + str(notebook_name_counter)
            notebook_name_list.append(notebook.notebook_name)

            notebook.notebook_dest = Core.get_notebook_destination(notebooks_destination, notebook.notebook_name)
            sections_dict = Core.notebook_check_section_json(notebook.notebook_root)
            nodes_dict = notebook.notebook_tree.set_note_tree(notebook.notebook_root, sections_dict)
            Paths.set_dest_path(notebook.notebook_dest, notebook.notebook_root)
            # 3.2 准备写入HTML
            # ----------------------------------------------------------------------------------------------------------
            # 3.2 Prepare to write html
            sections_dict = copy.deepcopy(nodes_dict)
            for key, node in sections_dict.items():
                sections_dict[key] = node.node_info_dict[NotebookProcessor.SECTION_DICT_NOTES_DICT]
            Core.prepare_file_writing()
            sections_dict = Core.write_converted_htmls(notebook, sections_dict)
            static_file_dict = Core.write_static_resources(notebook.statistic_files_dict)
            html_head = Core.generate_html_header(static_file_dict, sections_dict, notebook.notebook_name)
            html_body_head = Core.generate_html_body_head(static_file_dict)
            html_body_foot = Core.generate_html_body_foot(static_file_dict)
            # 3.3 开始写入HTML
            # ----------------------------------------------------------------------------------------------------------
            # 3.3 Start to write html file
            if Mode.is_local_mode():
                # 3.3.1 本地模式
                # ------------------------------------------------------------------------------------------------------
                # Step 1 生成并写入笔记本 index.html
                # Step 2 准备笔记本仓库 index.html
                # ------------------------------------------------------------------------------------------------------
                # 3.3.1 Local mode
                # ------------------------------------------------------------------------------------------------------
                # Step 1 Generate and write notebook's index.html
                # Step 2 Prepare notebook repository index.html
                html_body = Core.generate_local_html_body(html_body_head, html_body_foot, nodes_dict, sections_dict)
                Core.local_mode_write_index_html(html_head, html_body)
                Core.local_mode_del_static_files()
                # ------------------------------------------------------------------------------------------------------
                if Mode.is_r_local_mode():
                    # repo_note_dict
                    repository_html += "<a href = \"%s%s%s\">%s</a>\n" % \
                                       ("./", notebook.notebook_name, "/index.html", notebook.notebook_name)
            elif Mode.is_server_mode():
                # 3.3.2 服务器模式
                # ------------------------------------------------------------------------------------------------------
                # Step 1 写入 section-menu.blade.html
                # Step 2 为 "-rserver" 模式更新头文件，尾文件，.blade.html文件
                # Step 3 写入 .html 文件
                # Step 4 更新 lmain.js
                # Step 5 准备笔记本仓库 index.html
                # ------------------------------------------------------------------------------------------------------
                # 3.3.2 Server mode
                # ------------------------------------------------------------------------------------------------------
                # Step 1 Write section-menu.blade.html
                # Step 2 Update header/footer/all .blade.html files for "-rserver" mode
                # Step 3 Write .html file
                # Step 4 Update lmain.js
                # Step 5 Prepare notebook repository index.html
                with open(Paths.PATH_FULL_NOTEBOOK_DEST + "/source/section-menu.blade.html", "w+") as section_menu:
                    section_menu.write(nodes_dict[0].html_section_menu)
                # ------------------------------------------------------------------------------------------------------
                if Mode.is_r_server_mode():
                    html_head = __rserver_update(notebook, html_head)
                    html_body_foot = __rserver_update(notebook, html_body_foot)
                    for root, dirs, files in os.walk(Paths.PATH_FULL_NOTEBOOK_DEST):
                        for file in files:
                            dest_file = os.path.join(root, file)
                            if re.search(r"\.blade\.html$", dest_file):
                                with open(dest_file) as read_file:
                                    before = read_file.read()
                                    after = __rserver_update(notebook, before)
                                if before != after:
                                    with open(dest_file, "w+") as write_file:
                                        write_file.write(after)
                # ------------------------------------------------------------------------------------------------------
                index_section_id = None
                index_note_id = None
                for section_id, section_dict in sections_dict.items():
                    for note_id, note_dict in section_dict.items():
                        html_path_rel = note_dict[NotebookProcessor.NOTE_DICT_HTML_FILE_REL] + ".html"
                        html_body = Core.generate_server_html_body(html_body_head, html_body_foot, section_id, note_id)
                        Core.server_mode_write_page_html(html_path_rel, html_head, html_body)
                        if index_note_id is None and index_section_id is None:
                            index_section_id = section_id
                            index_note_id = note_id

                            inde_path = os.path.join(Paths.PATH_FULL_NOTEBOOK_DEST, "index.html")
                            note_path = os.path.join(Paths.PATH_FULL_NOTEBOOK_DEST, html_path_rel)
                            shutil.copy(note_path, inde_path)

                            note_blade_rel = note_dict[NotebookProcessor.NOTE_DICT_HTML_FILE_REL] + ".blade.html"
                            index_blade = os.path.join(Paths.PATH_FULL_NOTEBOOK_DEST, "index.blade.html")
                            note_blade = os.path.join(Paths.PATH_FULL_NOTEBOOK_DEST, note_blade_rel)
                            shutil.copy(note_blade, index_blade)
                # ------------------------------------------------------------------------------------------------------
                # !!!!!!不能硬写入
                main_js_location = os.path.join(notebook.notebook_dest, "source/js/smain.js")
                with open(main_js_location, "r+") as main_js:
                    js = main_js.read()
                with open(main_js_location, "w+") as main_js:
                    if Mode.is_r_server_mode():
                        main_js.write(("let prefix = \"/%s\";\n" % notebook.notebook_name) + js)
                    elif Mode.is_server_mode():
                        main_js.write("let prefix = \"\";\n" + js)
                    else:
                        raise Exception
                # ------------------------------------------------------------------------------------------------------
                if Mode.is_r_server_mode():
                    # repo_note_dict
                    repository_html += "<a href = \"%s%s%s\">%s</a>\n" % \
                                       ("/", notebook.notebook_name, "/index.html", notebook.notebook_name)
            else:
                logging.critical("Mode not exist! System Exit!")
                sys.exit(1)
        # 3.3 如果现在为仓库模式，为 所有笔记 模式写入 index.html
        # ----------------------------------------------------------------------------------------------------------
        # 3.3 Write index.html for all notebook if current mode is in Repository mode
        if Mode.is_r_local_mode():
            local_note_books_dest = notebooks_destination + "/local"
            with open(os.path.join(local_note_books_dest, "index.html"), "w+") as repository_file:
                repository_file.write(repository_html)
        elif Mode.is_r_server_mode():
            local_note_books_dest = notebooks_destination + "/server"
            with open(os.path.join(local_note_books_dest, "index.html"), "w+") as repository_file:
                repository_file.write(repository_html)

    else:
        logging.critical("Mode not exist! System Exit!")
        sys.exit(1)


# 📕 核心功能
# 为"-reserver"模式更新本地连接
# ----------------------------------------------------------------------------------------------------------------------
# 📕 Core function
# Update local link for "-reserver" mode
def __rserver_update(notebook, file_txt):
    link_match = re.search(r"((?<=src=\")|(?<=href=\"))(?=/source)", file_txt)
    while link_match:
        start = file_txt[:link_match.start()]
        end = file_txt[link_match.end():]
        file_txt = start + "/" + notebook.notebook_name + end
        link_match = re.search(r"((?<=src=\")|(?<=href=\"))(?=/source)", file_txt)
    return file_txt


if __name__ == '__main__':
    main()
