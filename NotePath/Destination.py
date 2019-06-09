import json
import logging
import os
import sys

from NotePath.BaiZeSys import BaiZeSys


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
                if Destination.PATH_FULL_SYS == os.path.commonpath([note_books_repo_path_full, Destination.PATH_FULL_SYS]):
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
    def __check_notebooks_dest_sub_folders(note_books_dest_path_full):
        for sub_folder in Destination.BAIZE_REPO_SUB_FOLDERS_LIST:
            sub_folder = os.path.join(note_books_dest_path_full, sub_folder)
            if not os.path.exists(sub_folder):
                os.mkdir(sub_folder)
