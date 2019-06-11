import json
import logging
import os
import re
import shutil
import sys

from HTML.HTML import HTML
from NotePath.BaiZeSys import BaiZeSys
from NotePath.Source import Source
from Tools import URIReplacement
from Tools.File import File
import emarkdown.markdown as md


class Destination:
    BAIZE_REPO_NAME = "BaiZeNote"
    BAIZE_REPO_SUB_FOLDERS_LIST = ["server", "local", "server/sources", "local/sources"]

    PATH_RELA_NOTEBOOKS_REPO_LOCATION_JSON = BaiZeSys.PATH_RELA_NOTEBOOKS_REPO_LOCATION_JSON
    NOTEBOOKS_REPO_LOCATION_KEY = BaiZeSys.NOTEBOOKS_REPO_LOCATION_KEY
    PATH_FULL_SYS = BaiZeSys.PATH_FULL_SYS

    @staticmethod
    def get_notebooks_destination():
        note_book_dest = ""
        note_books_repository = Destination.get_notebooks_repository()
        if "-d" in sys.argv:
            try:
                note_book_dest_index = sys.argv.index("-d") + 1
                note_book_dest = sys.argv[note_book_dest_index]
                note_book_dest = os.path.abspath(note_book_dest)
                if not os.path.exists(note_book_dest):
                    os.mkdir(note_book_dest)
                    Destination.__check_notebooks_dest_sub_folders(note_book_dest)
                if not os.access(note_book_dest, os.W_OK):
                    raise PermissionError
            except IndexError:
                logging.error("Notebook destination folder did not input!")
                logging.warning("Will use system default destination folder \"%s\". Do you want continue?(y/n)"
                                % note_books_repository)
                if input().lower() not in ["yes", "y"]:
                    return
                else:
                    note_book_dest = note_books_repository
            except PermissionError:
                logging.error("Notebook destination folder \"%s\" permission error!" % note_book_dest)
                logging.warning("Will use system default destination folder \"%s\". Do you want continue?(y/n)"
                                % note_books_repository)
                if input().lower() not in ["yes", "y"]:
                    return
                else:
                    note_book_dest = note_books_repository
        else:
            note_book_dest = note_books_repository
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
        note_book_repo_json_path_full = os.path.join(Destination.PATH_FULL_SYS,
                                                     Destination.PATH_RELA_NOTEBOOKS_REPO_LOCATION_JSON)
        if not os.path.isfile(note_book_repo_json_path_full):
            note_books_repo_path_full = Destination.initial_notebooks_repository()
        else:
            try:
                note_books_repo_json_file = open(note_book_repo_json_path_full, "r")
                note_books_repo_dict = json.loads(note_books_repo_json_file.read())
                note_books_repo_path_full = note_books_repo_dict[Destination.NOTEBOOKS_REPO_LOCATION_KEY]
                if not os.path.exists(note_books_repo_path_full):
                    os.mkdir(note_books_repo_path_full)
                if not os.access(note_books_repo_path_full, os.W_OK):
                    raise PermissionError
                else:
                    Destination.__check_notebooks_dest_sub_folders(note_books_repo_path_full)
            except PermissionError:
                logging.error("Permission denied! Please set a new notebooks repository!")
                os.remove(os.path.join(Destination.PATH_FULL_SYS, Destination.PATH_RELA_NOTEBOOKS_REPO_LOCATION_JSON))
                note_books_repo_path_full = Destination.initial_notebooks_repository()
            except IndexError:
                logging.error("BaiZe notebooks' repository config damaged! Please set a new notebooks repository!")
                os.remove(os.path.join(Destination.PATH_FULL_SYS, Destination.PATH_RELA_NOTEBOOKS_REPO_LOCATION_JSON))
                note_books_repo_path_full = Destination.initial_notebooks_repository()
        return note_books_repo_path_full

    @staticmethod
    def initial_notebooks_repository():
        while True:
            try:
                note_books_repo_path_full_raw = input("Please input a all notebooks repository folder:\n")
                note_books_repo_path_full = os.path.join(note_books_repo_path_full_raw, Destination.BAIZE_REPO_NAME)
                if Destination.PATH_FULL_SYS == os.path.commonpath(
                        [note_books_repo_path_full, Destination.PATH_FULL_SYS]):
                    raise PermissionError

                if os.path.exists(note_books_repo_path_full):
                    logging.warning(
                        "\"%s\" exists, do you still want use this folder as all notebooks' repository? (y/n)"
                        % note_books_repo_path_full)
                    if input().lower() in ["y", "yes"]:
                        pass
                    else:
                        continue
                else:
                    os.mkdir(note_books_repo_path_full)

                if not os.access(note_books_repo_path_full, os.W_OK):
                    raise PermissionError

                all_note_books_dest_dict = {
                    Destination.NOTEBOOKS_REPO_LOCATION_KEY: note_books_repo_path_full}
                note_books_repo_json_file_path_full = \
                    os.path.join(Destination.PATH_FULL_SYS, Destination.PATH_RELA_NOTEBOOKS_REPO_LOCATION_JSON)
                note_books_repo_json_file = open(note_books_repo_json_file_path_full, "w+")
                note_books_repo_json_file.write(json.dumps(all_note_books_dest_dict))
                note_books_repo_json_file.close()
                break
            except PermissionError:
                logging.error("Permission denied! Please enter another notebooks repository destination")
            except FileNotFoundError:
                logging.error("Folder location denied! Please enter another notebooks repository destination")

        Destination.__check_notebooks_dest_sub_folders(note_books_repo_path_full)
        return note_books_repo_path_full

    @staticmethod
    def prepare_file_writing(notebook_resource, notebook_destination):
        if os.path.exists(notebook_destination):
            shutil.rmtree(notebook_destination)
        File.folder_tree_copy(notebook_resource, notebook_destination)
        return

    @staticmethod
    def server_mode_write_converted_htmls(notebook, nodes_dict):
        # TODO What to do when note status lock / hide tag/reference and so on
        # TODO 后面emarkdown改了以后，generate 和 写入要分开
        copy_list = []
        for section_id, section_dict in nodes_dict.items():
            note_rel_list = []
            for note_id, note_dict in section_dict.items():
                note_rel_raw = note_dict[Source.SOURCE_SUB_NOTE_DICT_NOTE_FILE_PATH_REL]
                note_file_type = note_dict[Source.SOURCE_SUB_NOTE_DICT_NOTE_FILE_TYPE]
                note_html_rel_raw = re.sub("%s$" % note_file_type, "", note_rel_raw, 1)
                next_name_counter = 0
                while note_html_rel_raw in note_rel_list:
                    note_html_rel_raw += str(next_name_counter)
                note_html_path_rel = "%s%s" % (note_html_rel_raw, ".html")
                note_html_resource_path_full = os.path.join(notebook.notebook_root, note_rel_raw)

                note_html_destination_path_full = os.path.join(notebook.notebook_dest, note_html_path_rel)
                note_html_destination_path_full += ".blade.html"

                note_dict[Source.SOURCE_SUB_NOTE_DICT_HTML_FILE_REL] = note_html_path_rel

                if note_file_type == ".md":
                    md.process(["-f", note_html_resource_path_full, "-d", note_html_destination_path_full])
                    html_file = open(note_html_destination_path_full, "r")
                    raw_html_code = html_file.read()
                    html_file.close()
                    parent_path = "%s" % os.path.dirname(note_html_path_rel)
                    html_code = URIReplacement.replace_img_uri(raw_html_code, parent_path, copy_list)
                    if raw_html_code != html_code:
                        html_file = open(note_html_destination_path_full, "w+")
                        html_file.write(html_code)
                        html_file.close()
        for file in copy_list:
            file_source = os.path.join(notebook.notebook_root, file)
            file_destin = os.path.join(notebook.notebook_dest, file)
            try:
                shutil.copy(file_source, file_destin)
            except FileNotFoundError:
                logging.warning("Local file %s not found!" % file)
        return nodes_dict

    @staticmethod
    def server_mode_write_body_htmls(notebook, nodes_dict, html_head):
        for section_id, section_dict in nodes_dict.items():
            for note_id, note_dict in section_dict.items():
                html_path_rel = note_dict[Source.SOURCE_SUB_NOTE_DICT_HTML_FILE_REL]
                html_path_full = os.path.join(notebook.notebook_dest, html_path_rel)
                html_body = HTML.generate_server_body(section_id, note_id)
                html_file = open(html_path_full, "w+")
                html_file.write(html_head)
                html_file.write(html_body)
                html_file.close()

    @staticmethod
    def server_mode_write_static_resources(note_book, nodes_dict):
        notes_dest_path_full = note_book.notebook_dest
        files_dest_path_full = os.path.join(notes_dest_path_full, HTML.dest_path_rel)
        # 准备目标文件夹下的 source 静态文件夹
        if os.path.exists(files_dest_path_full):
            shutil.rmtree(files_dest_path_full)
        os.mkdir(files_dest_path_full)

        # 获取 "/source/all" 和 "/source/server" 下文件夹
        if "-server" in sys.argv:
            static_file_current_mode_path_rel = HTML.static_file_in_lib_path_rel_server_mode
        elif "-local" in sys.argv:
            static_file_current_mode_path_rel = HTML.static_file_in_lib_path_rel_local_mode
        else:
            logging.error("HTML output type is required")
            raise Exception

        static_path_full_all_mode = os.path.join(os.getcwd(), HTML.static_file_in_lib_path_relative_all_mode)
        static_path_current_mode = os.path.join(os.getcwd(), static_file_current_mode_path_rel)

        File.tree_merge_copy(static_path_full_all_mode, files_dest_path_full)
        File.tree_merge_copy(static_path_current_mode, files_dest_path_full)

        head_html = HTML.generate_head(note_book, nodes_dict)
        head_html_file = open(os.path.join(files_dest_path_full, HTML.dest_file_name_head_html), "w+")
        head_html_file.write(head_html)
        head_html_file.close()
        section_menu_html_file = open(os.path.join(files_dest_path_full, HTML.dest_file_name_section_menu_html), "w+")
        node_root_id = note_book.notebook_tree.node_id_root
        section_menu_html_file.write(note_book.notebook_tree.nodes_dict[node_root_id].html_section_menu)
        section_menu_html_file.close()
        return head_html



    @staticmethod
    def __check_notebooks_dest_sub_folders(note_books_dest_path_full):
        for sub_folder in Destination.BAIZE_REPO_SUB_FOLDERS_LIST:
            sub_folder = os.path.join(note_books_dest_path_full, sub_folder)
            if not os.path.exists(sub_folder):
                os.mkdir(sub_folder)
