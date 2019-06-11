import copy
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
            sections_info_dicts = Processor.source_check_section_json(notebook.notebook_root)
            nodes_dict = notebook.notebook_tree.set_note_tree(notebook.notebook_root, ".", sections_info_dicts)

            Processor.prepare_file_writing(notebook.notebook_root, notebook.notebook_dest)
            if "-local" in sys.argv:
                pass
            elif "-server" in sys.argv:
                # 处理 node dict
                nodes_dict = copy.deepcopy(nodes_dict)
                for key, node in nodes_dict.items():
                    nodes_dict[key] = node.node_info_dict[Source.SOURCE_SECTION_DICT_NOTES_DICT]
                nodes_dict = Processor.server_mode_write_converted_htmls(notebook, nodes_dict)
                html_head = Processor.server_mode_write_static_resources(notebook, nodes_dict)
                Processor.server_mode_write_body_htmls(notebook, nodes_dict, html_head)
                pass
    else:
        raise Exception
    return

    #     # 处理html
    #     print()
    # if "-local" in sys.argv:
    #     # 生成 <head> 部分，（包括 <head> 标签， 脚本/CSS 将直接写入到 index.html）
    #     # Generate <head> part (include <head> tag, and scripts/css will write into index.html directly)
    #     header_html = HTML.generate_head(note, section_md_info_dict)
    #     body_html = HTML.generate_local_body(section_menu_content_html, note.note_name)
    #     note_file = open(note.note_root + "/index.html", "w+")
    #     html = "%s%s" % (header_html, body_html)
    #     note_file.write(html)
    #     note_file.close()


if __name__ == '__main__':
    main()
