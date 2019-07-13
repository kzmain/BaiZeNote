import copy
import json
import logging
import os
import re
import shutil
import sys
from pathlib import Path

from Processor.Constants.Paths import Paths
from Processor.Constants import Constants
from Processor.HTMLProcessor import HTMLProcessor
from Processor.NotebookProcessor import NotebookProcessor
from Tools import URI, Mode
from Tools.File import File
import emarkdown.markdown as md


class DestinationProcessor:
    BAIZE_REPO_SUB_FOLDERS_LIST = ["server", "local"]

    # Get the processing notebook(s) destination
    # It has two mode:
    #   1. Enter a specific notebook destination
    #   2. Use default notebook destination
    # 获取即将处理的笔记本的目标地
    #   1. 输入一个指定即将要处理的笔记目标路径
    #   2. 使用默认笔记本目标路径
    # @Return:
    # note_book_dest: All notebooks destination
    # note_book_dest: 所有笔记本的目的地
    @staticmethod
    def get_notebooks_destination():
        note_book_dest = ""
        note_books_dest_default = DestinationProcessor.get_notebooks_repository()
        if "-d" in sys.argv:
            try:
                note_book_dest_index = sys.argv.index("-d") + 1
                note_book_dest = sys.argv[note_book_dest_index]
                note_book_dest = os.path.abspath(note_book_dest)
                if not os.path.exists(note_book_dest):
                    os.mkdir(note_book_dest)
                    DestinationProcessor.__check_notebooks_dest_sub_folders(note_book_dest)
                if not os.access(note_book_dest, os.W_OK):
                    raise PermissionError
            except IndexError:
                logging.error("Notebook destination folder did not input!")
                logging.warning("Will use system default destination folder \"%s\". Do you want continue?(y/n)"
                                % note_books_dest_default)
                if input().lower() not in ["yes", "y"]:
                    return
                else:
                    note_book_dest = note_books_dest_default
            except PermissionError:
                logging.error("Notebook destination folder \"%s\" permission error!" % note_book_dest)
                logging.warning("Will use system default destination folder \"%s\". Do you want continue?(y/n)"
                                % note_books_dest_default)
                if input().lower() not in ["yes", "y"]:
                    return
                else:
                    note_book_dest = note_books_dest_default
        else:
            note_book_dest = note_books_dest_default
        return note_book_dest

    @staticmethod
    def get_notebook_destination(note_books_dest, notebook_name):
        if Mode.is_local_mode():
            note_book_dest = os.path.join(note_books_dest, "local", notebook_name)
        elif Mode.is_server_mode():
            note_book_dest = os.path.join(note_books_dest, "server", notebook_name)
        else:
            raise Exception
        return note_book_dest

    @staticmethod
    def get_notebooks_repository():
        note_book_repo_json_path_full = Paths.PATH_FULL_NOTEBOOKS_DEST_LOCATION_JSON
        if not os.path.isfile(note_book_repo_json_path_full):
            note_books_repo_path_full = DestinationProcessor.initial_notebooks_repository()
        else:
            try:
                note_books_repo_json_file = open(note_book_repo_json_path_full, "r")
                note_books_repo_dict = json.loads(note_books_repo_json_file.read())
                note_books_repo_path_full = note_books_repo_dict[Constants.NOTEBOOKS_REPO_LOCATION_KEY]
                if not os.path.exists(note_books_repo_path_full):
                    os.mkdir(Path(note_books_repo_path_full).parent)
                    os.mkdir(note_books_repo_path_full)
                if not os.access(note_books_repo_path_full, os.W_OK):
                    raise PermissionError
                else:
                    DestinationProcessor.__check_notebooks_dest_sub_folders(note_books_repo_path_full)
            except PermissionError:
                logging.error("Permission denied! Please set a new notebooks repository!")
                os.remove(note_book_repo_json_path_full)
                note_books_repo_path_full = DestinationProcessor.initial_notebooks_repository()
            except IndexError:
                logging.error("BaiZe notebooks' repository config damaged! Please set a new notebooks repository!")
                os.remove(note_book_repo_json_path_full)
                note_books_repo_path_full = DestinationProcessor.initial_notebooks_repository()
        return note_books_repo_path_full

    @staticmethod
    def initial_notebooks_repository():
        while True:
            try:
                notebooks_repo_path_full_raw = input("Please input all notebooks default destination folder:\n")
                notebooks_repo_path_full = os.path.join(notebooks_repo_path_full_raw, Constants.BAIZE_REPO_NAME)
                if Paths.PATH_FULL_SYS_LOCATION == os.path.commonpath(
                        [notebooks_repo_path_full, Paths.PATH_FULL_SYS_LOCATION]):
                    raise PermissionError

                if os.path.exists(notebooks_repo_path_full):
                    logging.warning(
                        "\"%s\" exists, do you still want use this folder as all notebooks' repository? (y/n)"
                        % notebooks_repo_path_full)
                    if input().lower() in ["y", "yes"]:
                        pass
                    else:
                        logging.error("Please enter a new notebooks repository destination.")
                else:
                    os.mkdir(notebooks_repo_path_full_raw)
                    os.mkdir(notebooks_repo_path_full)

                if not os.access(notebooks_repo_path_full, os.W_OK):
                    raise PermissionError

                all_note_books_dest_dict = \
                    {Constants.NOTEBOOKS_REPO_LOCATION_KEY: notebooks_repo_path_full}
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

        DestinationProcessor.__check_notebooks_dest_sub_folders(notebooks_repo_path_full)
        return notebooks_repo_path_full

    @staticmethod
    def prepare_file_writing():
        if os.path.exists(Paths.PATH_FULL_NOTEBOOK_DEST):
            shutil.rmtree(Paths.PATH_FULL_NOTEBOOK_DEST)
        File.folder_tree_copy(Paths.PATH_FULL_NOTEBOOK_REPOSITORY, Paths.PATH_FULL_NOTEBOOK_DEST)

    # @staticmethod
    # def local_mode_write_converted_htmls(notebook, nodes_dict):
    #     # TODO What to do when note status lock / hide tag/reference and so on
    #     # TODO 后面emarkdown改了以后，generate 和 写入要分开
    #     image_dict = {}
    #     for section_id, section_dict in nodes_dict.items():
    #         note_rel_list = []
    #         for note_id, note_dict in section_dict.items():
    #             note_rel_raw = note_dict[NotebookProcessor.NOTE_DICT_NOTE_FILE_PATH_REL]
    #             note_file_type = note_dict[NotebookProcessor.NOTE_DICT_NOTE_FILE_TYPE]
    #             note_html_rel_raw = re.sub("%s$" % note_file_type, "", note_rel_raw, 1)
    #             next_name_counter = 0
    #             while note_html_rel_raw in note_rel_list:
    #                 note_html_rel_raw += str(next_name_counter)
    #             note_html_path_rel = "%s%s" % (note_html_rel_raw, ".html")
    #             note_html_resource_path_full = os.path.join(notebook.notebook_root, note_rel_raw)
    #
    #             note_html_destination_path_full = os.path.join(notebook.notebook_dest, note_html_path_rel)
    #             note_html_destination_path_full += ".blade.html"
    #
    #             note_dict[NotebookProcessor.NOTE_DICT_HTML_FILE_REL] = note_html_path_rel
    #
    #             if note_file_type == ".md":
    #                 md.process(["-f", note_html_resource_path_full, "-d", note_html_destination_path_full])
    #                 html_file = open(note_html_destination_path_full, "r")
    #                 raw_html = html_file.read()
    #                 html_file.close()
    #
    #                 note_folder_res = os.path.dirname(note_html_resource_path_full)
    #                 html_code = \
    #                     URI.replace_local_mode_img_uri(raw_html, note_folder_res, image_dict, notebook.notebook_root)
    #
    #                 if raw_html != html_code:
    #                     html_file = open(note_html_destination_path_full, "w+")
    #                     html_file.write(html_code)
    #                     html_file.close()
    #     notebook.statistic_files_dict["images"] = image_dict
    #     return nodes_dict

    @staticmethod
    def write_converted_htmls(notebook, nodes_dict):
        # TODO What to do when note status lock / hide tag/reference and so on
        # TODO 后面emarkdown改了以后，generate 和 写入要分开
        # TODO 对PDF和WORD等支持
        # !!!!!!!!TODO audio video
        image_dict = {}
        media_dict = {}
        iter_dict = copy.deepcopy(nodes_dict)
        for section_id, section_dict in iter_dict.items():
            note_rel_list = []
            for note_id, note_dict in section_dict.items():
                # 1. Get correct file destination file name
                # 如果不转换 a.md 和 a.pdf 都会变为 a.html
                note_file_type = note_dict[NotebookProcessor.NOTE_DICT_NOTE_FILE_TYPE]
                note_res_rel = note_dict[NotebookProcessor.NOTE_DICT_NOTE_FILE_PATH_REL]
                note_html_rel = re.sub("%s$" % note_file_type, "", note_res_rel, 1)
                next_name_counter = 0
                while note_html_rel in note_rel_list:
                    note_html_rel += str(next_name_counter)
                # 2. Store html file location to note_dict
                # note_html_path_rel = "%s%s" % (note_html_rel, ".html")
                nodes_dict[section_id][note_id][NotebookProcessor.NOTE_DICT_HTML_FILE_REL] = note_html_rel
                # 3. Write html files
                res_path = os.path.join(notebook.notebook_root, note_res_rel)
                dest_path = os.path.join(notebook.notebook_dest, note_html_rel + ".blade.html")

                file_dict = {".md": DestinationProcessor.__md_to_html}
                try:
                    # !!!!! 故意输入非md
                    html = file_dict[note_file_type](res_path, dest_path, image_dict, media_dict)
                    nodes_dict[section_id][note_id]["HTML"] = html
                except IndexError:
                    logging.critical("File %s cannot process" % res_path)
                    # md.process(["-f", res_path, "-d", dest_path])
                    # html_file = open(dest_path, "r")
                    # raw_html = html_file.read()
                    # html_file.close()
                    #
                    # note_folder_res = os.path.dirname(res_path)
                    # html_code = URI.replace_server_mode_img_uri(raw_html, note_folder_res, image_dict)
                    #
                    # if raw_html != html_code:
                    #     html_file = open(dest_path, "w+")
                    #     html_file.write(html_code)
                    #     html_file.close()
        notebook.statistic_files_dict["images"] = image_dict
        notebook.statistic_files_dict["media"] = media_dict
        return nodes_dict

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

    @staticmethod
    def local_mode_write_body_htmls(html_head, html_body):
        html_path_full = os.path.join(Paths.PATH_FULL_NOTEBOOK_DEST, "index.html")
        html_file = open(html_path_full, "w+")
        html_file.write(html_head)
        html_file.write(html_body)
        html_file.close()

    @staticmethod
    def server_mode_write_body_htmls(nodes_dict, html_head, html_foot):
        for section_id, section_dict in nodes_dict.items():
            for note_id, note_dict in section_dict.items():
                html_path_rel = note_dict[NotebookProcessor.NOTE_DICT_HTML_FILE_REL] + ".html"
                html_path_full = os.path.join(Paths.PATH_FULL_NOTEBOOK_DEST, html_path_rel)
                html_body = HTMLProcessor.generate_server_body(html_foot, section_id, note_id)
                html_file = open(html_path_full, "w+")
                html_file.write(html_head)
                html_file.write(html_body)
                html_file.close()

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

    @staticmethod
    def write_static_resources(files_dict):

        # 1. 准备目标文件夹下的 source 静态文件夹
        if os.path.exists(Paths.PATH_FULL_NOTEBOOK_RESOURCE_DEST):
            shutil.rmtree(Paths.PATH_FULL_NOTEBOOK_RESOURCE_DEST)
        os.mkdir(Paths.PATH_FULL_NOTEBOOK_RESOURCE_DEST)
        # 1.1 转换的静态文件
        for static_type, file_type_dict in files_dict.items():
            os.mkdir(os.path.join(Paths.PATH_FULL_NOTEBOOK_RESOURCE_DEST, static_type))
            for res_path_full, dest_path_rel in file_type_dict.items():
                dest_path_full = os.path.join(Paths.PATH_FULL_NOTEBOOK_RESOURCE_DEST, static_type, dest_path_rel)
                shutil.copy(res_path_full, dest_path_full)
        # 2. 获取 "/source/all" 和 "/source/server" 下文件夹
        if Mode.is_server_mode():
            static_rel = HTMLProcessor.static_rel_server_mode
        elif Mode.is_local_mode():
            static_rel = HTMLProcessor.static_rel_local_mode
        else:
            logging.error("HTML output type is required")
            raise Exception
        # 3. 拷贝系统基础scripts
        sys_static_full = os.path.join(Paths.PATH_FULL_SYS_LOCATION, static_rel)
        File.tree_merge_copy(sys_static_full, Paths.PATH_FULL_NOTEBOOK_RESOURCE_DEST)
        # !!!!!!!!! 会出Exception 在选 themes的时候
        # 4. 拷贝自定义scripts
        while True:
            theme_loc = DestinationProcessor.__select_theme()
            static_files_dict = DestinationProcessor.__select_theme_mode()
            if len(static_files_dict) > 0:
                break

        for script_type, script_dict in static_files_dict.items():
            # for script_name, script_dict in theme_dict.items():
            for script_name, script_info_dict in script_dict.items():
                if not script_info_dict["remote"]:
                    res_path = os.path.join(theme_loc, script_info_dict["location"])
                    dest_path_full = os.path.join(Paths.PATH_FULL_NOTEBOOK_RESOURCE_DEST, script_info_dict["location"])
                    if not os.path.exists(Path(dest_path_full).parent):
                        os.mkdir(Path(dest_path_full).parent)
                    shutil.copy(res_path, dest_path_full)
        return static_files_dict
        # if "-thememode" in sys.argv:
        #     # !!!! 还有可能并无此mode
        #     try:
        #         theme_mode_index = sys.argv.index("-thememode") + 1
        #         theme_mode = sys.argv[theme_mode_index]
        #     except IndexError:
        #         theme_mode = "default"
        # else:
        #     theme_mode = "default"
        # with open(os.path.join(theme_loc, "libs.json")) as basic_json, \
        #         open(os.path.join(theme_loc, "footer.json")) as before_basic_json, \
        #         open(os.path.join(theme_loc, "header.json")) as after_basic_json:
        #     # basic_dict = json.loads(basic_json.read())
        #     other_themes_dicts = [
        #         json.loads(before_basic_json.read())[theme_mode],
        #         json.loads(basic_json.read()),
        #         json.loads(after_basic_json.read())[theme_mode]
        #     ]

        #
        # head_html = HTMLProcessor.generate_head(note_book, nodes_dict, static_files_dict, theme_mode)
        # head_html_file = open(os.path.join(Paths.PATH_FULL_NOTEBOOK_RESOURCE_DEST, HTMLProcessor.dest_file_name_head_html), "w+")
        # head_html_file.write(head_html)
        # head_html_file.close()
        # section_menu_html_file = open(
        #     os.path.join(Paths.PATH_FULL_NOTEBOOK_RESOURCE_DEST, HTMLProcessor.dest_file_name_section_menu_html), "w+")
        # node_root_id = note_book.notebook_tree.node_id_root
        # section_menu_html_file.write(note_book.notebook_tree.nodes_dict[node_root_id].html_section_menu)
        # section_menu_html_file.close()
        #
        # for file_type, file_dict in note_book.statistic_files_dict.items():
        #     dest_file_dir = os.path.join(Paths.PATH_FULL_NOTEBOOK_RESOURCE_DEST, file_type)
        #     if not os.path.exists(dest_file_dir):
        #         os.mkdir(dest_file_dir)
        #     for resource_file_path_full, dest_file_path_rel in file_dict.items():
        #         dest_file_path_full = os.path.join(Paths.PATH_FULL_NOTEBOOK_RESOURCE_DEST, file_type, dest_file_path_rel)
        #         try:
        #             shutil.copy(resource_file_path_full, dest_file_path_full)
        #         except FileNotFoundError:
        #             logging.warning("Local file %s not found!" % resource_file_path_full)
        # return head_html

    @staticmethod
    def __check_notebooks_dest_sub_folders(note_books_dest_path_full):
        for sub_folder in DestinationProcessor.BAIZE_REPO_SUB_FOLDERS_LIST:
            sub_folder = os.path.join(note_books_dest_path_full, sub_folder)
            if not os.path.exists(sub_folder):
                os.mkdir(sub_folder)
