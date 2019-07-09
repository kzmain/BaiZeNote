import json
import logging
import os
import re
import shutil
import sys
from pathlib import Path

from Processor.Constants import Paths
from Processor.Constants import Constants
from Processor.HTMLProcessor import HTMLProcessor
from Processor.NotebookProcessor import NotebookProcessor
from Tools import URI
from Tools.File import File
import emarkdown.markdown as md


class DestinationProcessor:
    BAIZE_REPO_SUB_FOLDERS_LIST = ["server", "local"]

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
        if "-local" in sys.argv:
            note_book_dest = os.path.join(note_books_dest, "local", notebook_name)
        elif "-server" in sys.argv:
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

        DestinationProcessor.__check_notebooks_dest_sub_folders(notebooks_repo_path_full)
        return notebooks_repo_path_full

    @staticmethod
    def prepare_file_writing(notebook_resource, notebook_destination):
        if os.path.exists(notebook_destination):
            shutil.rmtree(notebook_destination)
        File.folder_tree_copy(notebook_resource, notebook_destination)
        return

    @staticmethod
    def local_mode_write_converted_htmls(notebook, nodes_dict):
        # TODO What to do when note status lock / hide tag/reference and so on
        # TODO 后面emarkdown改了以后，generate 和 写入要分开
        image_dict = {}
        for section_id, section_dict in nodes_dict.items():
            note_rel_list = []
            for note_id, note_dict in section_dict.items():
                note_rel_raw = note_dict[NotebookProcessor.NOTE_DICT_NOTE_FILE_PATH_REL]
                note_file_type = note_dict[NotebookProcessor.NOTE_DICT_NOTE_FILE_TYPE]
                note_html_rel_raw = re.sub("%s$" % note_file_type, "", note_rel_raw, 1)
                next_name_counter = 0
                while note_html_rel_raw in note_rel_list:
                    note_html_rel_raw += str(next_name_counter)
                note_html_path_rel = "%s%s" % (note_html_rel_raw, ".html")
                note_html_resource_path_full = os.path.join(notebook.notebook_root, note_rel_raw)

                note_html_destination_path_full = os.path.join(notebook.notebook_dest, note_html_path_rel)
                note_html_destination_path_full += ".blade.html"

                note_dict[NotebookProcessor.NOTE_DICT_HTML_FILE_REL] = note_html_path_rel

                if note_file_type == ".md":
                    md.process(["-f", note_html_resource_path_full, "-d", note_html_destination_path_full])
                    html_file = open(note_html_destination_path_full, "r")
                    raw_html = html_file.read()
                    html_file.close()

                    note_folder_res = os.path.dirname(note_html_resource_path_full)
                    html_code = \
                        URI.replace_local_mode_img_uri(raw_html, note_folder_res, image_dict, notebook.notebook_root)

                    if raw_html != html_code:
                        html_file = open(note_html_destination_path_full, "w+")
                        html_file.write(html_code)
                        html_file.close()
        notebook.statistic_files_dict["images"] = image_dict
        return nodes_dict

    @staticmethod
    def server_mode_write_converted_htmls(notebook, nodes_dict):
        # TODO What to do when note status lock / hide tag/reference and so on
        # TODO 后面emarkdown改了以后，generate 和 写入要分开
        image_dict = {}
        for section_id, section_dict in nodes_dict.items():
            note_rel_list = []
            for note_id, note_dict in section_dict.items():
                note_rel_raw = note_dict[NotebookProcessor.NOTE_DICT_NOTE_FILE_PATH_REL]
                note_file_type = note_dict[NotebookProcessor.NOTE_DICT_NOTE_FILE_TYPE]
                note_html_rel_raw = re.sub("%s$" % note_file_type, "", note_rel_raw, 1)
                next_name_counter = 0
                while note_html_rel_raw in note_rel_list:
                    note_html_rel_raw += str(next_name_counter)
                note_html_path_rel = "%s%s" % (note_html_rel_raw, ".html")
                note_html_resource_path_full = os.path.join(notebook.notebook_root, note_rel_raw)

                note_html_destination_path_full = os.path.join(notebook.notebook_dest, note_html_path_rel)
                note_html_destination_path_full += ".blade.html"

                note_dict[NotebookProcessor.NOTE_DICT_HTML_FILE_REL] = note_html_path_rel

                if note_file_type == ".md":
                    md.process(["-f", note_html_resource_path_full, "-d", note_html_destination_path_full])
                    html_file = open(note_html_destination_path_full, "r")
                    raw_html_code = html_file.read()
                    html_file.close()

                    note_folder_resource = os.path.dirname(note_html_resource_path_full)
                    html_code = URI.replace_server_mode_img_uri(raw_html_code, note_folder_resource, image_dict)

                    if raw_html_code != html_code:
                        html_file = open(note_html_destination_path_full, "w+")
                        html_file.write(html_code)
                        html_file.close()
        notebook.statistic_files_dict["images"] = image_dict
        return nodes_dict

    @staticmethod
    def local_mode_write_body_htmls(notebook, html_head):
        html_path_full = os.path.join(notebook.notebook_dest, "index.html")
        html_file = open(html_path_full, "w+")
        section_menu = notebook.notebook_tree.nodes_dict[0].html_section_menu
        notebook_name = notebook.notebook_name
        html_body = HTMLProcessor.generate_local_body(section_menu, notebook_name)
        html_file.write(html_head)
        html_file.write(html_body)
        html_file.close()

    @staticmethod
    def server_mode_write_body_htmls(notebook, nodes_dict, html_head):
        for section_id, section_dict in nodes_dict.items():
            for note_id, note_dict in section_dict.items():
                html_path_rel = note_dict[NotebookProcessor.NOTE_DICT_HTML_FILE_REL]
                html_path_full = os.path.join(notebook.notebook_dest, html_path_rel)
                html_body = HTMLProcessor.generate_server_body(section_id, note_id)
                html_file = open(html_path_full, "w+")
                html_file.write(html_head)
                html_file.write(html_body)
                html_file.close()

    @staticmethod
    def write_static_resources(note_book, nodes_dict):
        notes_dest_path_full = note_book.notebook_dest
        files_dest_path_full = os.path.join(notes_dest_path_full, HTMLProcessor.dest_path_rel)
        # 准备目标文件夹下的 source 静态文件夹
        if os.path.exists(files_dest_path_full):
            shutil.rmtree(files_dest_path_full)
        os.mkdir(files_dest_path_full)

        # 获取 "/source/all" 和 "/source/server" 下文件夹
        if "-server" in sys.argv:
            static_file_current_mode_path_rel = HTMLProcessor.static_file_in_lib_path_rel_server_mode
        elif "-local" in sys.argv:
            static_file_current_mode_path_rel = HTMLProcessor.static_file_in_lib_path_rel_local_mode
        else:
            logging.error("HTML output type is required")
            raise Exception
        # !!!!!!!!! 会出Exception 在选 themes的时候
        static_path_current_mode = \
            os.path.join(Paths.PATH_FULL_SYS_LOCATION, static_file_current_mode_path_rel)

        File.tree_merge_copy(static_path_current_mode, files_dest_path_full)

        with open(Paths.PATH_FULL_NOTEBOOKS_THEME_JSON) as theme_config:
            theme_name = json.loads(theme_config.read())["current"]
        theme_loc = os.path.join(Paths.PATH_FULL_SYS_LOCATION, "source/themes", theme_name)
        if "-thememode" in sys.argv:
            # !!!! 还有可能并无此mode
            try:
                theme_mode_index = sys.argv.index("-thememode") + 1
                theme_mode = sys.argv[theme_mode_index]
            except IndexError:
                theme_mode = "default"
        else:
            theme_mode = "default"
        with open(os.path.join(theme_loc, "basic.json")) as basic_json, \
                open(os.path.join(theme_loc, "before_basic.json")) as before_basic_json, \
                open(os.path.join(theme_loc, "after_basic.json")) as after_basic_json:
            # basic_dict = json.loads(basic_json.read())
            other_themes_dicts = [
                json.loads(before_basic_json.read())[theme_mode],
                json.loads(basic_json.read()),
                json.loads(after_basic_json.read())[theme_mode]
            ]

            for theme_dict in other_themes_dicts:
                for script_name, script_dict in theme_dict.items():
                    if not script_dict["remote"]:
                        res_path = os.path.join(theme_loc, script_dict["location"])
                        dest_path = os.path.join(files_dest_path_full, script_dict["location"])
                        if not os.path.exists(Path(dest_path).parent):
                            os.mkdir(Path(dest_path).parent)
                        shutil.copy(res_path, dest_path)

        head_html = HTMLProcessor.generate_head(note_book, nodes_dict, theme_name, theme_mode)
        head_html_file = open(os.path.join(files_dest_path_full, HTMLProcessor.dest_file_name_head_html), "w+")
        head_html_file.write(head_html)
        head_html_file.close()
        section_menu_html_file = open(
            os.path.join(files_dest_path_full, HTMLProcessor.dest_file_name_section_menu_html), "w+")
        node_root_id = note_book.notebook_tree.node_id_root
        section_menu_html_file.write(note_book.notebook_tree.nodes_dict[node_root_id].html_section_menu)
        section_menu_html_file.close()

        for file_type, file_dict in note_book.statistic_files_dict.items():
            dest_file_dir = os.path.join(files_dest_path_full, file_type)
            if not os.path.exists(dest_file_dir):
                os.mkdir(dest_file_dir)
            for resource_file_path_full, dest_file_path_rel in file_dict.items():
                dest_file_path_full = os.path.join(files_dest_path_full, file_type, dest_file_path_rel)
                try:
                    shutil.copy(resource_file_path_full, dest_file_path_full)
                except FileNotFoundError:
                    logging.warning("Local file %s not found!" % resource_file_path_full)
        return head_html

    @staticmethod
    def __check_notebooks_dest_sub_folders(note_books_dest_path_full):
        for sub_folder in DestinationProcessor.BAIZE_REPO_SUB_FOLDERS_LIST:
            sub_folder = os.path.join(note_books_dest_path_full, sub_folder)
            if not os.path.exists(sub_folder):
                os.mkdir(sub_folder)
