import os
import re
import shutil
import sys
import time
import logging
import json
from pathlib import Path

from HTML.HTML import HTML
from NotePath.Processor import Processor
from NotePath.Source import Source
from Notebook import Notebook

from Tools.File import File
from source.temp.svg.SVG import SVG
import emarkdown.markdown as md

from Tools import URIReplacement


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

    # "-n" 模式，创建一个新的笔记仓库
    # "-n" mode make a new note repository
    if "-n" in sys.argv:
        # 1. 获取笔记名称
        # 1. Get notebook name
        try:
            note_book_name_index = sys.argv.index("-n") + 1
            note.notebook_root = sys.argv[note_book_name_index]
            note.notebook_name = os.path.basename(note.notebook_root)
        except IndexError:
            logging.error("Notebook name is required after \"-c\".")
            return
        # 2. 创建笔记仓库
        # 2. Create notebook folder (Repository)
        try:
            os.mkdir(note.notebook_root)
        except FileExistsError:
            # 如果笔记的文件夹已经存在
            # If note folder already exist
            logging.warning("NoteBook repository has already existed.")
        # 3. 写入 .notebook.json 到笔记根目录
        # 3. Write .notebook.json to notebook's root folder
        if os.path.exists(os.path.join(note.notebook_root + Path.notebook_json_path_relative)):
            logging.error("NoteBook config has already set before.")
        else:
            write_notebook_json(note.notebook_root)
        return
    # Generate note book
    elif "-g" in sys.argv:
        # 1. 获取需要转换的 所有 笔记本的路径,有新的写入系统，有失效的从系统删除
        notebooks_list = Processor.sys_get_processing_notebooks_list()
        notebooks_list = Processor.sys_check_notebooks_validation(notebooks_list)
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
            notebook.notebook_dict = Processor.sys_get_notebooks_info()[notebook_path]
            sections_info_dicts= Processor.source_check_section_json(notebook.notebook_root)

            if os.path.exists(notebook.notebook_dest):
                shutil.rmtree(notebook.notebook_dest)
            File.folder_tree_copy(notebook.notebook_root, notebook.notebook_dest)

            # 处理html

        # 3. 初始化每个笔记
        #   Task 1 获取每个 文件夹/.md文件 信息
        #   Task 2 将 .md 文件转换为 .html 文件
        #   ！！！！！！！！！Task 3 Write ".dir_list.json" and ".file_list.json" to EACH folder
        note = initial_files_and_sections(note, os.path.relpath(note.notebook_root, note.notebook_root))

        # 4. 获取最后 .html 文件相关信息
        #     Task 1 获取 section menu html
        #     Task 2 获取 section_id-md_id 对应信息
        # 4. Get final .html related info
        #     Task 1 Get section menu html
        #     Task 2 Get section_id-md_id pair infos
        # 4 Task 1
        root_node = note.note_tree.go_to_node(0)
        section_menu_content_html = root_node.html
        # 4 Task 2
        section_md_info_dict = {}
        for section_number, section_node in note.note_tree.tree_nodes_dict.items():
            section_md_info_dict["section%s" % section_number] = section_node.md_dict
        # 5 生成最后 html 静态文件，有 "-server"， "-local" 两种模式
        #     "-local" 模式，将 scripts、css、所有 md 转换 html 结果等全部写入到 index.html 文件中
        #     "-server" 模式，将大部分的 scripts，css 写入到 /source 文件夹中，每个 md 生成在不同文件夹中生成其对应 html 文件
        if "-local" in sys.argv:
            # 生成 <head> 部分，（包括 <head> 标签， 脚本/CSS 将直接写入到 index.html）
            # Generate <head> part (include <head> tag, and scripts/css will write into index.html directly)
            header_html = HTML.generate_head(note, section_md_info_dict)
            body_html = HTML.generate_local_body(section_menu_content_html, note.note_name)
            note_file = open(note.note_root + "/index.html", "w+")
            html = "%s%s" % (header_html, body_html)
            note_file.write(html)
            note_file.close()
        elif "-server" in sys.argv:

            # 生成 <head> 部分，（包括 <head> 标签，脚本/CSS将用外部引入的形式写入到 index.html）
            # Generate <head> (include <header> tag, and scripts/css will referenced by link type)
            header_html = HTML.generate_head(note, section_md_info_dict)
            # 生成 <body> <div id="section_menu"> 的内容 (不！包括 <div id="section_menu"> tag)
            # Generate <body> <div id="section_menu"> 's content (does NOT include <div id="section_menu"> tag)
            section_menu_path_full = os.path.join(note.note_root, HTML.static_file_dest_path_rel,
                                                  "section-menu.blade.html")
            section_menu_html_file = open(section_menu_path_full, "w+")
            section_menu_html_file.write(section_menu_content_html)
            section_menu_html_file.close()
            # 根据对应的 .md 文件生成对应的 HTML 页面
            # Generate HTML pages for corresponding .md files
            for section_id, section_dict in note.note_tree.tree_nodes_dict.items():
                for note_id, note_dict in section_dict.md_dict.items():
                    html_path_full = os.path.abspath(note.note_book_dest + note_dict["html_path_relative"])
                    html_file = open(html_path_full, "w+")
                    html_file.write(header_html + HTML.generate_server_body("section%s" % section_id, note_id))
                    html_file.close()
    else:
        raise Exception


# # ！！！！！！！！！！！！！前半部分需要分割！因为写入以后才知道上次更改时间
# # 📕1. 核心任务：
# #   1.1. 将 ".notebook.json" 写入到笔记根目录,这包含笔记本的所有的信息
# # ----------------------------------------------------------------------------------------------------------------------
# # 📕1. Core tasks:
# #   1.1. Write ".notebook.json" in note root folder, This include basic info of notebook
# def write_notebook_json(note_book_root_location):
#     # c_datetime = datetime.datetime.now()
#     # current_date = "%s-%s-%s" % (c_datetime.year, c_datetime.month, c_datetime.day)
#     # current_time = "%s:%s:%s:%s" % (c_datetime.hour, c_datetime.minute, c_datetime.second, c_datetime.microsecond)
#     # note_name = os.path.basename(note_book_root_location)
#     # 情况 2 如果 .notebook.json 存在则添加最新更改时间
#     # Circumstance 2 if .notebook.json exists add current update time
#     # note_book_config_json_full_path = os.path.join(note_book_root_location, Source.SOURCE_PATH_REL_NOTEBOOK_JSON)
#     notebooks_config_full_path = os.path.join(NoteSys.PATH_FULL_SYS, NoteSys.PATH_RELA_NOTEBOOKS_JSON)
#     notebooks_config_file = open(notebooks_config_full_path, "r")
#     notebooks_config_dict = json.loads(notebooks_config_file.read())
#     if note_book_root_location in notebooks_config_dict:
#         # ！！！！！！！要只用r+覆盖
#         note_book_json_file = open(note_book_config_json_full_path, "r")
#         note_book_dict = json.loads(note_book_json_file.read())
#         note_book_json_file.close()
#         note_book_json_file = open(note_book_config_json_full_path, "w+")
#         new_ctime = time.ctime(os.path.getmtime(note_book_config_json_full_path))
#         if new_ctime not in note_book_dict["Modification_Time"]:
#             note_book_dict["Modification_Time"].append(new_ctime)
#             note_book_json_file.write(json.dumps(note_book_dict))
#         note_book_json_file.close()
#     # 情况 2 如果 .notebook.json 不存在,则初始化写入信息到 .notebook.json
#     # Circumstance 2 if .notebook.json does NOT exist, write initial info to .notebook.json
#     else:
#         while True:
#             enter_author_string = "Please input notebook name, if multiple author please separate by comma \",\" : \n"
#             confirm_author_string = "Is(Are) following your notebook's author(s) name(s)?(y/n)\n%s\n"
#             author_raw = input(enter_author_string)
#             author_list = author_raw.split(",")
#             author_list = [x for x in author_list if x.strip()]
#             if input(confirm_author_string % str(author_list)).lower() in ["yes", "y"]:
#                 break
#         note_book_dict = {"Author": author_list, "Note_Name": os.path.basename(note_book_root_location),
#                           "Creation_time": time.ctime(os.path.getctime(note_book_config_json_full_path)),
#                           "Modification_Time": [time.ctime(os.path.getmtime(note_book_config_json_full_path))]
#                           }
#     NoteSys.sys_add_a_notebook(note_book_root_location, note_book_dict)
#     return note_book_dict








# 📕1. 核心任务
#   1.1. 获取当前 section 的相关信息
#   1.2. 生成 .md 文件对应的 html，"-server" 模式会写入，"-local" 模式会写入后删除
# 📗2. section_info_dict 结构
# ！！！To be continue
# 📘3. 相关function
#   3.1. md_to_htm()
# ----------------------------------------------------------------------------------------------------------------------
# 📕1. Core Tasks
#   1.1. Get current section's related info
#   1.2. Generate html for each current folder's .md files,
#   "-server" mode will write html, "-local" mode will write html first then remove it later
# 📗2. section_info_dict structure
# ！！！To be continue
# 📘3. Related function
#   3.1. md_to_htm()
def write_section_info_dict(note, target_section_path_relative):
    target_section_path_abs = os.path.abspath(os.path.join(note.note_root, target_section_path_relative))
    # 获取本文件夹1级子*文件*及*文件夹*的名字
    # Get Level 1 *sub-folders* and *files* name
    dir_file_list = os.listdir(target_section_path_abs)
    # 分离出1级*文件夹（section）*和*.md 文件*
    # Split Level 1 "*Folders (sections)* and *.md files*
    section_md_list_dict = {"section": [], "md": []}
    for dir_file in dir_file_list:
        element_path = "%s/%s" % (target_section_path_abs, dir_file)
        if os.path.isdir(element_path):
            section_md_list_dict["section"].append(dir_file)
        else:
            if ".md" in element_path:
                section_md_list_dict["md"].append(dir_file)
    # 排序 "section" 名字，排序 "md" 名字
    # Sort name of "section" and "md"
    # ！！！！！！！！！！！！可更改，读取本地顺序，如果没有则添加
    section_md_list_dict["section"].sort(reverse=True)
    section_md_list_dict["md"].sort()
    # 获取本 section 相关信息 （本function核心部分）
    # Get section related info (Core part of this function)
    section_info_dict = \
        {"section_path_relative": target_section_path_relative,
         "section_name": os.path.basename(target_section_path_abs),
         "md": {}, "section": {}}
    for inclusion_type, inclusion_list in section_md_list_dict.items():
        count = 0
        inclusion_dict = {}
        for inclusion_name in inclusion_list:
            element_path_relative = os.path.join(target_section_path_relative, inclusion_name)
            element_info_dict = {"%s_name" % inclusion_type: inclusion_name}
            # element_info_dict["creation_time"]= os.path.getctime()
            if inclusion_type == "md":
                html_name = re.sub(r"\.md$", ".html", inclusion_name)
                html_path_relative = os.path.join(target_section_path_relative, html_name)
                # !!!!!!!!!!!----------------------------------------------------------------------------------------------------
                html_path_relative = html_path_relative.replace("./", "/", 1)
                # 写入/获取 HTML 代码
                # Write html/Get HTML codes
                html_code_md = md_to_html(note, element_path_relative, target_section_path_relative)

                element_info_dict["html_name"] = html_name
                element_info_dict["html_path_relative"] = html_path_relative
                if "-local" in sys.argv:
                    element_info_dict["html_code"] = html_code_md
            inclusion_dict["%s%s" % (inclusion_type, count)] = element_info_dict
            count += 1
        section_info_dict[inclusion_type] = inclusion_dict
    section_json_file_path_full = os.path.join(target_section_path_abs, ".section_info.json")
    section_json_file = open(section_json_file_path_full, "w+")
    section_json_file.write(json.dumps(section_info_dict))
    return section_info_dict


# 📕1. 核心任务
#   1.1. 写入/获取 .md 文件对应的 HTML
#       "-server" 模式将直接写入硬盘。（注意💥这个模式需要处理链接本地的图片）！！！！！其实影片，链接也需要处理
#       "-local" 模式将写入硬盘后，读取，在删除
# ----------------------------------------------------------------------------------------------------------------------
# 📕1. Core Tasks
#   1.1. Write/Get .md's corresponding HTML,
#       "-server" mode will write to hard disk directly,(Notice💥 this mode need re-process links to local image files)
#       "-local" mode will write it to hard disk first then read it then remove it
def md_to_html(note, file_relative_location, folder_path_relative):
    # 处理 .md，生成对应 .html文件
    # Process .md file, generate it corresponding .html file
    md_file_path_full = os.path.abspath(os.path.join(note.note_root, file_relative_location))
    md.process(["-f", md_file_path_full])
    # 打开本地对应 HTML 文件，读取 HTML 文件对应 .md 文件
    # Open local html files and read .md file's .html
    html_path_relative = re.sub(r"\.md$", ".html", file_relative_location)
    html_file_path_full = os.path.abspath(os.path.join(note.note_root, html_path_relative))
    html_file = open(html_file_path_full, "r")
    html_code = html_file.read()
    html_file.close()
    if "-local" in sys.argv:
        html_code = URIReplacement.replace_img_uri(html_code, folder_path_relative)
        os.remove(html_file_path_full)
    if "-server" in sys.argv:
        os.rename(html_file_path_full, html_file_path_full + ".note.html")
    return html_code


# 📕1. 核心任务
#   1.1. 处理当前 node 的section menu
#       当前 node 的section menu 应该包含其子node的section menu
# 📗2. Section menu 类型
#   2.1 有 sub-section （不管其是否有笔记）
#   2.2 没有 sub-section 但有笔记
#   2.3 没有 sub-section 没有笔记
# ----------------------------------------------------------------------------------------------------------------------
# 📕1. Core Tasks
#   1.1. Process current node's section menu
#       current node's section menu need also contains it's sub-nodes' section
# 📗2.Section menu has three types:
#   2.1. Has sub-section (no matter if has notes)
#   2.2. Has NO sub-section and has notes
#   2.3. Has NO sub-section and has NO notes
def process_section_menu(note_tree):
    current_node = note_tree.current_node
    # 1. 有 sub-section （不管其是否有笔记）
    # 1. Has sub-section (no matter if has notes)
    if len(current_node.section_dict) > 0:
        current_node_child_nodes_list = current_node.childNodesIds.copy()
        child_nodes_html = ""
        # 收集子section 的 section-menu
        # Gather sub-section's section menu
        for node_id in current_node_child_nodes_list:
            child_nodes_html += note_tree.tree_nodes_dict[node_id].html
        # 当本 node 不为 root node 时，生成此 node 的 section menu
        # If current node is not root node, generate current node's section menu
        if current_node.name != "Index":
            current_node.html = \
                HTML.sections_span % (
                    current_node.nodeId, current_node.nodeId, current_node.nodeId, SVG.sections_svg,
                    current_node.name, current_node.nodeId, child_nodes_html
                )
        else:
            current_node.html = child_nodes_html
    # 2. 没有 sub-section 但有笔记
    # 2. Has NO sub-section and has notes
    elif len(current_node.section_dict) == 0 and len(current_node.md_dict) > 0:
        current_node.html = HTML.no_sections_span % \
                            (current_node.nodeId, current_node.nodeId, SVG.no_sections_svg, current_node.name)
    # 3. 没有 sub-section 没有笔记
    # 3. Has NO sub-section and has NO notes
    else:
        current_node.html = \
            HTML.no_notes_no_sections_span % \
            (current_node.nodeId, current_node.nodeId, SVG.no_notes_no_sections_svg, current_node.name)
    note_tree.current_node = current_node
    return note_tree


if __name__ == '__main__':
    main()
