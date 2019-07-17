import copy
import json
import logging
import os
import re
import shutil
import sys
from pathlib import Path

import emarkdown.markdown as md

from Processor.Constants import Constants, NotebooksDict, NotebookDict, SysArgument
from Processor.Constants.Paths import Paths
from Tools import URI, Mode
from Tools.File import File


class DestinationProcessor:
    # TODO 如果servermode不要生成local
    BAIZE_REPO_SUB_FOLDERS_LIST = ["server", "local"]

    # 📕 核心功能
    # 获取所有笔记本输出文件夹
    #   1. 输入一个指定即将要处理的笔记目标路径
    #   2. 使用默认笔记本目标路径
    # ⬇️ 参数
    # None
    # ⬆️ 返回值
    # dest: 所有笔记本输出文件夹
    # ------------------------------------------------------------------------------------------------------------------
    # 📕 Core function
    # Get ALL notebook output folders
    # It has two mode:
    #   1. Enter a specific notebook destination
    #   2. Use default notebook destination
    # ⬇️ Parameter:
    # None
    # ⬆️ Return
    # dest: ALL notebook output folders
    @staticmethod
    def get_notebooks_destination():
        dest = ""
        dest_default = DestinationProcessor.__get_notebooks_default_repository()
        if SysArgument.NOTEBOOKS_DESTINATION_FLAG in sys.argv:
            try:
                note_book_dest_index = sys.argv.index(SysArgument.NOTEBOOKS_DESTINATION_FLAG) + 1
                dest = sys.argv[note_book_dest_index]
                dest = os.path.abspath(dest)
                if not os.path.exists(dest):
                    os.mkdir(dest)
                    DestinationProcessor.__check_notebooks_dest_sub_folders(dest)
                if not os.access(dest, os.W_OK):
                    raise PermissionError
            except IndexError:
                logging.error("Notebook destination folder did not input!")
                logging.warning("Will use system default destination folder \"%s\". Do you want continue?(y/n)"
                                % dest_default)
                if input().lower() not in ["yes", "y"]:
                    return
                else:
                    dest = dest_default
            except PermissionError:
                logging.error("Notebook destination folder \"%s\" permission error!" % dest)
                logging.warning("Will use system default destination folder \"%s\". Do you want continue?(y/n)"
                                % dest_default)
                if input().lower() not in ["yes", "y"]:
                    return
                else:
                    dest = dest_default
        else:
            dest = dest_default
        return dest

    # 📕 核心功能
    # 获取当前笔记本输出文件夹
    # ⬇️ 参数
    # note_books_dest: 所有笔记本的输出文件夹
    # notebook_name: 当前笔记本名称
    # ⬆️ 返回值
    # note_book_dest: 当前笔记本输出文件夹
    # ------------------------------------------------------------------------------------------------------------------
    # 📕 Core function
    # Get CURRENT notebook output folders
    # ⬇️ Parameter:
    # note_books_dest: ALL notebooks output file path
    # notebook_name: Current notebook name
    # ⬆️ Return
    # note_book_dest: CURRENT notebook output folders
    @staticmethod
    def get_notebook_destination(note_books_dest, notebook_name):
        if Mode.is_local_mode():
            note_book_dest = os.path.join(note_books_dest, "local", notebook_name)
        elif Mode.is_server_mode():
            note_book_dest = os.path.join(note_books_dest, "server", notebook_name)
        else:
            raise Exception
        return note_book_dest

    # 📕 核心功能
    # 获取默认笔记本输出文件夹
    # ⬇️ 参数
    # None
    # ⬆️ 返回值
    # default_path_full: 默认笔记本输出文件夹
    # 🎯应用:
    # DestinationProcessor.get_notebooks_destination()
    # ------------------------------------------------------------------------------------------------------------------
    # 📕 Core function
    # Get DEFAULT notebook output folders
    # ⬇️ Parameter:
    # None
    # ⬆️ Return
    # default_path_full: DEFAULT notebook output folders
    # 🎯Usage:
    # DestinationProcessor.get_notebooks_destination()
    @staticmethod
    def __get_notebooks_default_repository():
        note_book_repo_json_path_full = Paths.PATH_FULL_NOTEBOOKS_DEST_LOCATION_JSON
        if not os.path.isfile(note_book_repo_json_path_full):
            default_path_full = DestinationProcessor.initial_notebooks_repository()
        else:
            try:
                note_books_repo_json_file = open(note_book_repo_json_path_full, "r")
                note_books_repo_dict = json.loads(note_books_repo_json_file.read())
                default_path_full = note_books_repo_dict[NotebooksDict.NOTEBOOKS_REPO_LOCATION_KEY]
                if not os.path.exists(default_path_full):
                    os.mkdir(Path(default_path_full).parent)
                    os.mkdir(default_path_full)
                if not os.access(default_path_full, os.W_OK):
                    raise PermissionError
                else:
                    DestinationProcessor.__check_notebooks_dest_sub_folders(default_path_full)
            except PermissionError:
                logging.error("Permission denied! Please set a new notebooks repository!")
                os.remove(note_book_repo_json_path_full)
                default_path_full = DestinationProcessor.initial_notebooks_repository()
            except IndexError:
                logging.error("BaiZe notebooks' repository config damaged! Please set a new notebooks repository!")
                os.remove(note_book_repo_json_path_full)
                default_path_full = DestinationProcessor.initial_notebooks_repository()
        return default_path_full

    # 📕 核心功能
    # 初始化默认笔记本输出文件夹
    # ⬇️ 参数
    # None
    # ⬆️ 返回值
    # default_repo: 默认笔记本输出文件夹
    # ------------------------------------------------------------------------------------------------------------------
    # 📕 Core function
    # Initial DEFAULT notebook output folders
    # ⬇️ Parameter:
    # None
    # ⬆️ Return
    # default_repo: DEFAULT notebook output folders
    @staticmethod
    def initial_notebooks_repository():
        while True:
            try:
                notebooks_repo_path_full_raw = input("Please input all notebooks default destination folder:\n")
                default_repo = os.path.join(notebooks_repo_path_full_raw, Constants.BAIZE_REPO_NAME)
                if Paths.PATH_FULL_SYS_LOCATION == os.path.commonpath(
                        [default_repo, Paths.PATH_FULL_SYS_LOCATION]):
                    raise PermissionError

                if os.path.exists(default_repo):
                    logging.warning(
                        "\"%s\" exists, do you still want use this folder as all notebooks' repository? (y/n)"
                        % default_repo)
                    if input().lower() in ["y", "yes"]:
                        pass
                    else:
                        logging.error("Please enter a new notebooks repository destination.")
                else:
                    os.mkdir(notebooks_repo_path_full_raw)
                    os.mkdir(default_repo)

                if not os.access(default_repo, os.W_OK):
                    raise PermissionError

                all_note_books_dest_dict = \
                    {NotebooksDict.NOTEBOOKS_REPO_LOCATION_KEY: default_repo}
                note_books_repo_json_file_path_full = Paths.PATH_FULL_NOTEBOOKS_DEST_LOCATION_JSON
                note_books_repo_json_file = open(note_books_repo_json_file_path_full, "w+")
                note_books_repo_json_file.write(json.dumps(all_note_books_dest_dict))
                note_books_repo_json_file.close()
                break
            except PermissionError:
                logging.error("Permission denied! Please enter another notebooks repository destination")
            except FileNotFoundError:
                logging.error("Folder location denied! Please enter another notebooks repository destination")
            except ValueError:
                logging.error("Wrong path value! Please enter another notebooks repository destination")

        DestinationProcessor.__check_notebooks_dest_sub_folders(default_repo)
        return default_repo

    # 📕 核心功能
    # 准备写入目标文件夹
    # ⬇️ 参数
    # None
    # ⬆️ 返回值
    # None
    # ------------------------------------------------------------------------------------------------------------------
    # 📕 Core function
    # Prepare to write to the destination folder
    # ⬇️ Parameter:
    # None
    # ⬆️ Return
    # None
    @staticmethod
    def prepare_file_writing():
        if os.path.exists(Paths.PATH_FULL_NOTEBOOK_DEST):
            shutil.rmtree(Paths.PATH_FULL_NOTEBOOK_DEST)
        File.folder_tree_copy(Paths.PATH_FULL_NOTEBOOK_REPOSITORY, Paths.PATH_FULL_NOTEBOOK_DEST)

    # 📕 核心功能
    # 将支持的文件格式笔记从笔记本源文件文件夹转化成HTML笔记到目标文件夹
    # ⬇️ 参数
    # notebook: 内存中的Notebook
    # nodes_dict: 所有的nodes信息字典
    # ⬆️ 返回值
    # nodes_dict: 所有的nodes信息字典
    # ------------------------------------------------------------------------------------------------------------------
    # 📕 Core function
    # Convert supported file format notes from notebook source file folder to html notes to destination folder
    # ⬇️ Parameter:
    # notebook: Notebook in memory
    # nodes_dict: dictionary for all nodes
    # ⬆️ Return
    # nodes_dict: dictionary for all nodes
    @staticmethod
    def write_converted_htmls(notebook, nodes_dict):
        # TODO What to do when note status lock / hide tag/reference and so on
        # TODO 后面emarkdown改了以后，generate 和 写入要分开
        # TODO 对PDF和WORD等支持
        image_dict = {}
        media_dict = {}
        iter_dict = copy.deepcopy(nodes_dict)
        for section_id, section_dict in iter_dict.items():
            note_rel_list = []
            for note_id, note_dict in section_dict.items():
                # 1. Get correct file destination file name
                # 如果不转换 a.md 和 a.pdf 都会变为 a.html
                note_file_type = note_dict[NotebookDict.NOTE_DICT_NOTE_FILE_TYPE]
                note_res_rel = note_dict[NotebookDict.NOTE_DICT_NOTE_FILE_PATH_REL]
                note_html_rel = re.sub("%s$" % note_file_type, "", note_res_rel, 1)
                next_name_counter = 0
                while note_html_rel in note_rel_list:
                    note_html_rel += str(next_name_counter)
                # 2. Store html file location to note_dict
                # note_html_path_rel = "%s%s" % (note_html_rel, ".html")
                nodes_dict[section_id][note_id][NotebookDict.NOTE_DICT_HTML_FILE_REL] = note_html_rel
                # 3. Write html files
                res_path = os.path.join(notebook.notebook_root, note_res_rel)
                dest_path = os.path.join(notebook.notebook_dest, note_html_rel + ".blade.html")

                file_dict = {".md": DestinationProcessor.__md_to_html}
                try:
                    # !!!!! 故意输入非md
                    file_dict[note_file_type](res_path, dest_path, image_dict, media_dict)
                    # html = file_dict[note_file_type](res_path, dest_path, image_dict, media_dict)
                    # nodes_dict[section_id][note_id]["HTML"] = html
                except IndexError:
                    logging.critical("File %s cannot process" % res_path)
        notebook.statistic_files_dict["images"] = image_dict
        notebook.statistic_files_dict["media"] = media_dict
        return nodes_dict

    # 📕 核心功能
    # md笔记转换为html
    # ⬇️ 参数
    # res_path: 源文件路径
    # dest_path: 目标文件路径
    # image_dict: 图片文件字典
    # media_dict: 多媒体文件字典
    # ⬆️ 返回值
    # html_code: 转换后的笔记HTML代码
    # 🎯应用:
    # DestinationProcessor.write_converted_htmls()
    # ------------------------------------------------------------------------------------------------------------------
    # 📕 Core function
    # Convert .md notes to html notes
    # ⬇️ Parameter:
    # res_path: resource files full path
    # dest_path: destination files full path
    # image_dict: image files dictionary
    # media_dict: media files dictionary
    # ⬆️ Return
    # html_code: Converted note HTML code
    # 🎯Usage:
    # DestinationProcessor.write_converted_htmls()
    @staticmethod
    def __md_to_html(res_path, dest_path, image_dict, media_dict):
        md.process(["-f", res_path, "-d", dest_path])
        html_file = open(dest_path, "r")
        raw_html = html_file.read()
        html_file.close()

        note_folder_res = os.path.dirname(res_path)
        if Mode.is_server_mode():
            html_code = URI.replace_server_mode_img_uri(raw_html, note_folder_res, image_dict)
            html_code = URI.replace_server_mode_media_uri(html_code, note_folder_res, media_dict)
        elif Mode.is_local_mode():
            html_code = URI.replace_local_mode_img_uri(raw_html, note_folder_res, image_dict)
            html_code = URI.replace_local_mode_media_uri(html_code, note_folder_res, media_dict)
        else:
            raise Exception
        if raw_html != html_code:
            html_file = open(dest_path, "w+")
            html_file.write(html_code)
            html_file.close()
        return html_code

    # 📕 核心功能
    # "(-r)server" 模式写入html文件
    # ⬇️ 参数
    # html_path_rel: html文件相对位置
    # html_head: html头文件
    # html_body: html body 部分
    # ⬆️ 返回值
    # None
    # ------------------------------------------------------------------------------------------------------------------
    # 📕 Core function
    # "(-r)server" mode write html
    # ⬇️ Parameter:
    # html_path_rel: html relative location
    # html_head: html header
    # html_body: html body body
    # ⬆️ Return
    # None
    @staticmethod
    def server_mode_write_page_html(html_path_rel, html_head, html_body):
                html_path_full = os.path.join(Paths.PATH_FULL_NOTEBOOK_DEST, html_path_rel)
                html_file = open(html_path_full, "w+")
                html_file.write(html_head)
                html_file.write(html_body)
                html_file.close()

    # 📕 核心功能
    # "(-r)local" 模式写入html文件
    # ⬇️ 参数
    # html_head: html头文件
    # html_body: html body 部分
    # ⬆️ 返回值
    # None
    # ------------------------------------------------------------------------------------------------------------------
    # 📕 Core function
    # "(-r)local" mode write html
    # ⬇️ Parameter:
    # html_head: html header
    # html_body: html body body
    # ⬆️ Return
    # None
    @staticmethod
    def local_mode_write_index_html(html_head, html_body):
        html_path_full = os.path.join(Paths.PATH_FULL_NOTEBOOK_DEST, "index.html")
        html_file = open(html_path_full, "w+")
        html_file.write(html_head)
        html_file.write(html_body)
        html_file.close()

    # 📕 核心功能
    # 选择主题，并检查主题文件
    # ⬇️ 参数
    # None
    # ⬆️ 返回值
    # None
    # ------------------------------------------------------------------------------------------------------------------
    # 📕 Core function
    # check theme, and check theme files
    # ⬇️ Parameter:
    # None
    # ⬆️ Return
    # None
    @staticmethod
    def __select_theme():
        with open(Paths.PATH_FULL_NOTEBOOKS_THEME_JSON) as theme_config_file:
            theme_config = json.loads(theme_config_file.read())
            theme_name = theme_config["current"]
        theme_loc = os.path.join(Paths.PATH_FULL_SYS_LOCATION, "source/themes", theme_name)
        check_file = ["libs.json", "header.json", "footer.json"]
        for file in check_file:
            file_path = os.path.join(theme_loc, file)
            if file == "libs.json":
                if os.path.isfile(file_path):
                    pass
                else:
                    if theme_name == "default":
                        logging.critical("Your default theme's libs.json has problem please fix.")
                        sys.exit(1)
                    else:
                        continue
            # 如果文件不存在
            if not os.path.isfile(file_path):
                logging.critical("Your %s theme's %s has problem please fix." % (theme_name, file))
                if theme_name == "default":
                    sys.exit(1)
                else:
                    logging.critical("We will try default mode theme")
                    # TODO 如何使用短func
                    with open(Paths.PATH_FULL_NOTEBOOKS_THEME_JSON, "w+") as theme_config_file:
                        theme_config["current"] = "default"
                        theme_config_file.write(theme_config)
                        return DestinationProcessor.__select_theme()
            # 如果文件存在
            else:
                with open(file_path) as jfile:
                    try:
                        json.loads(jfile.read())
                    except json.decoder.JSONDecodeError:
                        logging.critical("Your %s theme's %s has problem please fix." % (theme_name, file))
                        logging.critical("We will try default mode theme")
                        # TODO 如何使用短func
                        with open(Paths.PATH_FULL_NOTEBOOKS_THEME_JSON, "w+") as theme_config_file:
                            theme_config["current"] = "default"
                            theme_config_file.write(theme_config)
                            return DestinationProcessor.__select_theme()
        return theme_loc

    # 📕 核心功能
    # 选择主题模式
    # ⬇️ 参数
    # None
    # ⬆️ 返回值
    # result: 需要的脚本文件字典
    # 格式: {"lib": {}, "head": {}, "foot": {}}
    # ------------------------------------------------------------------------------------------------------------------
    # 📕 Core function
    # select theme mode
    # ⬇️ Parameter:
    # None
    # ⬆️ Return
    # result: required scripts files dictionary
    # FORMAT: {"lib": {}, "head": {}, "foot": {}}
    @staticmethod
    def __select_theme_mode():
        result = {}
        with open(Paths.PATH_FULL_NOTEBOOKS_THEME_JSON) as theme_config_file:
            theme_config = json.loads(theme_config_file.read())
            theme_name = theme_config["current"]
        theme_loc = os.path.join(Paths.PATH_FULL_SYS_LOCATION, "source/themes", theme_name)
        default_theme_loc = os.path.join(Paths.PATH_FULL_SYS_LOCATION, "source/themes", "default")
        if "-thememode" in sys.argv:
            # !!!! 还有可能并无此mode
            try:
                theme_mode_index = sys.argv.index("-thememode") + 1
                theme_mode = sys.argv[theme_mode_index]
            except IndexError:
                theme_mode = "default"
        else:
            theme_mode = "default"
        lib_loc = os.path.join(theme_loc, "libs.json")
        foot_loc = os.path.join(theme_loc, "footer.json")
        head_loc = os.path.join(theme_loc, "header.json")
        if not os.path.isfile(lib_loc):
            lib_loc = os.path.join(default_theme_loc, "libs.json")

        with open(lib_loc) as lib_file, open(foot_loc) as footer_file, open(head_loc) as header_file:
            try:
                themes_dicts = {
                    "lib": json.loads(lib_file.read()),
                    "head": json.loads(header_file.read())[theme_mode],
                    "foot": json.loads(footer_file.read())[theme_mode]
                }
            except IndexError:
                if theme_name == "default" and theme_mode == "default":
                    logging.error("Default theme's config footer.json or header.json encounter problem! "
                                  "Please Fix! "
                                  "Exit!")
                    sys.exit(1)
                elif theme_name == "default" and theme_mode != "default":
                    logging.critical("Default theme's mode \"%s\" config footer.json or header.json encounter problem! "
                                     "We will try default theme's default mode" % theme_mode)
                    theme_mode_index = sys.argv.index("-thememode") + 1
                    sys.argv[theme_mode_index] = "default"
                    return DestinationProcessor.__select_theme_mode()
                else:
                    logging.critical("\"%s\" theme's mode \"%s\" config footer.json or header.json encounter problem! "
                                     "We will try default theme's default mode" %
                                     (theme_name[:1] + theme_name[1:], theme_mode))
                    theme_mode_index = sys.argv.index("-thememode") + 1
                    sys.argv[theme_mode_index] = "default"
                    with open(Paths.PATH_FULL_NOTEBOOKS_THEME_JSON, "w+") as theme_config_file:
                        theme_config["current"] = "default"
                        theme_config_file.write(theme_config)
                    return {}
            for script_type, script_info_dict in themes_dicts.items():
                result[script_type] = {}
                for file_name, file_dict in script_info_dict.items():
                    result[script_type][file_name] = {}
                    if not file_dict["remote"]:
                        local_file = os.path.join(theme_loc, file_dict["location"])
                        if not os.path.isfile(local_file):
                            if theme_name == "default" and theme_mode == "default":
                                logging.error("Default theme's file \"%s\" missed! "
                                              "Please Fix! "
                                              "Exit!"
                                              % os.path.join(Paths.PATH_FULL_SYS_LOCATION, file_dict["location"]))
                                sys.exit(1)
                            elif theme_name == "default" and theme_mode != "default":
                                logging.critical(
                                    "Default theme's mode \"%s\" file \"%s\" missed! "
                                    "We will try default theme's default mode" %
                                    (theme_mode, os.path.join(Paths.PATH_FULL_SYS_LOCATION, file_dict["location"])))
                                theme_mode_index = sys.argv.index("-thememode") + 1
                                sys.argv[theme_mode_index] = "default"
                                return DestinationProcessor.__select_theme_mode()
                            else:
                                logging.critical(
                                    "\"%s\" theme's mode \"%s\" file \"%s\" missed! "
                                    "We will try default theme's default mode" %
                                    (theme_name[:1] + theme_name[1:], theme_mode,
                                     os.path.join(Paths.PATH_FULL_SYS_LOCATION, file_dict["location"])))
                                theme_mode_index = sys.argv.index("-thememode") + 1
                                sys.argv[theme_mode_index] = "default"
                                with open(Paths.PATH_FULL_NOTEBOOKS_THEME_JSON, "w+") as theme_config_file:
                                    theme_config["current"] = "default"
                                    theme_config_file.write(theme_config)
                                return {}
                    result[script_type][file_name]["remote"] = file_dict["remote"]
                    result[script_type][file_name]["location"] = file_dict["location"]
                    result[script_type][file_name]["type"] = file_dict["type"]
        return result

    # 📕 核心功能
    # 写入scripts文件到目标文件夹
    # ⬇️ 参数
    # script_files_dict: 脚本字典
    # ⬆️ 返回值
    # script_files_dict: 脚本字典
    # 格式: {"lib": {}, "head": {}, "foot": {}}
    # ------------------------------------------------------------------------------------------------------------------
    # 📕 Core function
    # Write scripts to output dictionary
    # ⬇️ Parameter:
    # script_files_dict: script files dictionary
    # ⬆️ Return
    # script_files_dict: script files dictionary
    # FORMAT: {"lib": {}, "head": {}, "foot": {}}
    @staticmethod
    def write_static_resources(script_files_dict):
        # 1. 准备目标文件夹下的 source 静态文件夹
        if os.path.exists(Paths.PATH_FULL_NOTEBOOK_SCRIPTS_DEST):
            shutil.rmtree(Paths.PATH_FULL_NOTEBOOK_SCRIPTS_DEST)
        os.mkdir(Paths.PATH_FULL_NOTEBOOK_SCRIPTS_DEST)
        # 1.1 转换的静态文件
        for static_type, file_type_dict in script_files_dict.items():
            os.mkdir(os.path.join(Paths.PATH_FULL_NOTEBOOK_SCRIPTS_DEST, static_type))
            for res_path_full, dest_path_rel in file_type_dict.items():
                dest_path_full = os.path.join(Paths.PATH_FULL_NOTEBOOK_SCRIPTS_DEST, static_type, dest_path_rel)
                try:
                    shutil.copy(res_path_full, dest_path_full)
                except FileNotFoundError:
                    logging.critical("File \"%s\" not found" % res_path_full)
        # 2. 获取 "/source/all" 和 "/source/server" 下文件夹
        if Mode.is_server_mode():
            static_rel = Paths.PATH_RELA_SCRIPT_FILES_SERVER_MODE
        elif Mode.is_local_mode():
            static_rel = Paths.PATH_RELA_SCRIPT_FILES_LOCAL_MODE
        else:
            logging.error("HTML output type is required")
            raise Exception
        # 3. 拷贝系统基础scripts
        sys_static_full = os.path.join(Paths.PATH_FULL_SYS_LOCATION, static_rel)
        File.tree_merge_copy(sys_static_full, Paths.PATH_FULL_NOTEBOOK_SCRIPTS_DEST)
        # 4. 拷贝自定义scripts
        while True:
            theme_loc = DestinationProcessor.__select_theme()
            static_files_dict = DestinationProcessor.__select_theme_mode()
            if len(static_files_dict) > 0:
                break

        for script_type, script_dict in static_files_dict.items():
            for script_name, script_info_dict in script_dict.items():
                if not script_info_dict["remote"]:
                    res_path = os.path.join(theme_loc, script_info_dict["location"])
                    dest_path_full = os.path.join(Paths.PATH_FULL_NOTEBOOK_SCRIPTS_DEST, script_info_dict["location"])
                    if not os.path.exists(Path(dest_path_full).parent):
                        os.mkdir(Path(dest_path_full).parent)
                    shutil.copy(res_path, dest_path_full)
        banner_jpg = os.path.join(Paths.PATH_FULL_NOTEBOOK_REPOSITORY, "banner.jpg")
        banner_jpg_dest = os.path.join(Paths.PATH_FULL_NOTEBOOK_DEST, "source/system/banner.jpg")
        banner_png = os.path.join(Paths.PATH_FULL_NOTEBOOK_REPOSITORY, "banner.png")
        banner_png_dest = os.path.join(Paths.PATH_FULL_NOTEBOOK_DEST, "source/system/banner.png")
        banner_png_sys = os.path.join(Paths.PATH_FULL_SYS_LOCATION, "source/system/banner.png")
        banner_png_sys_dest = os.path.join(Paths.PATH_FULL_NOTEBOOK_DEST, "source/system/banner.png")
        if os.path.isfile(banner_jpg):
            res = banner_jpg
            dest = banner_jpg_dest
        elif os.path.isfile(banner_png):
            res = banner_png
            dest = banner_png_dest
            shutil.copy(banner_png, banner_png_dest)
        else:
            res = banner_png_sys
            dest = banner_png_sys_dest
        if not os.path.exists(Path(dest).parent):
            os.mkdir(Path(dest).parent)
        shutil.copy(res, dest)
        ico = os.path.join(Paths.PATH_FULL_NOTEBOOK_REPOSITORY, "favicon.ico")
        ico_dest = os.path.join(Paths.PATH_FULL_NOTEBOOK_DEST, "source/system/favicon.ico")
        ico_sys = os.path.join(Paths.PATH_FULL_SYS_LOCATION, "source/system/favicon.ico")
        ico_sys_dest = os.path.join(Paths.PATH_FULL_NOTEBOOK_DEST, "source/system/favicon.ico")
        if os.path.isfile(ico):
            res = ico
            dest = ico_dest
        else:
            res = ico_sys
            dest = ico_sys_dest
        if not os.path.exists(Path(dest).parent):
            os.mkdir(Path(dest).parent)
        shutil.copy(res, dest)
        return static_files_dict

    # 📕 核心功能
    # 生成目标文件夹的local/server文件夹
    # ⬇️ 参数
    # note_books_dest_path_full: 所有笔记本的输出文件夹
    # ⬆️ 返回值
    # None
    # 🎯应用:
    # DestinationProcessor.get_notebooks_destination()
    # DestinationProcessor.__get_notebooks_default_repository()
    # DestinationProcessor.initial_notebooks_repository()
    # ------------------------------------------------------------------------------------------------------------------
    # 📕 Core function
    # Convert .md notes to html notes
    # ⬇️ Parameter:
    # note_books_dest_path_full: All notebooks output file folders
    # ⬆️ Return
    # None
    # 🎯Usage:
    # DestinationProcessor.get_notebooks_destination()
    # DestinationProcessor.__get_notebooks_default_repository()
    # DestinationProcessor.initial_notebooks_repository()
    @staticmethod
    def __check_notebooks_dest_sub_folders(note_books_dest_path_full):
        for sub_folder in DestinationProcessor.BAIZE_REPO_SUB_FOLDERS_LIST:
            sub_folder = os.path.join(note_books_dest_path_full, sub_folder)
            if not os.path.exists(sub_folder):
                os.mkdir(sub_folder)

    # 📕 核心功能
    # 删除 "-(r)local" 模式多余的静态文件（主要包括：.js/.css/section-menu.blade.html, .html.blade）
    # ⬇️ 输入参数
    # None
    # ⬆️ 返回值
    # None
    # ------------------------------------------------------------------------------------------------------------------
    # 📕 Core function
    # Delete extra static files in "-(r)local" mode (mainly include .js/.css/section-menu.blade.html, .html.blade)
    # ⬇️ Input argument
    # None
    # ⬆️ Return
    # none
    @staticmethod
    def local_mode_del_static_files():
        all_list = os.listdir(Paths.PATH_FULL_NOTEBOOK_DEST)
        all_list += ["source/js", "source/css"]
        for element in all_list:
            path = os.path.join(Paths.PATH_FULL_NOTEBOOK_DEST, element)
            if os.path.isfile(path):
                if element == "index.html":
                    continue
                os.remove(path)
            else:
                if element == "source":
                    continue
                shutil.rmtree(path)
