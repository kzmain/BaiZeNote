import json
import logging
import os
import shutil
import sys
import time
from datetime import datetime


# import Notebook


class BaiZeSys:
    PATH_FULL_SYS = os.path.abspath(os.curdir)

    PATH_RELA_NOTEBOOKS_REPO_LOCATION_JSON = "configs/note_books_repo_location.json"
    PATH_RELA_NOTEBOOKS_JSON = "configs/note_books_repo_all_notebooks.json"
    PATH_FULL_NOTEBOOKS_JSON = os.path.join(PATH_FULL_SYS, PATH_RELA_NOTEBOOKS_JSON)

    NOTEBOOKS_REPO_LOCATION_KEY = "NOTE_BOOKS_REPO_PATH_FULL"

    sys_configs_check_no_repo_loc = "no_repo_loc"

    @staticmethod
    def sys_configs_check():
        all_note_books_json_path_full = os.path.join(os.getcwd(), BaiZeSys.PATH_RELA_NOTEBOOKS_JSON)
        note_books_repo_loc_json_path_full = os.path.join(os.getcwd(), BaiZeSys.PATH_RELA_NOTEBOOKS_REPO_LOCATION_JSON)
        if not os.path.exists(all_note_books_json_path_full):
            all_note_books_json = open(all_note_books_json_path_full, "w+")
            all_note_books_json.write(json.dumps({}))
            all_note_books_json.close()
        if not os.path.exists(note_books_repo_loc_json_path_full):
            return BaiZeSys.sys_configs_check_no_repo_loc
        else:
            return ""

    @staticmethod
    def sys_add_a_notebook(note_book_path, note_book_info_dict):
        all_note_books_dict = BaiZeSys.sys_get_notebooks_info()
        if note_book_path not in all_note_books_dict:
            all_note_books_dict[note_book_path] = note_book_info_dict
            BaiZeSys.sys_set_notebooks_info(all_note_books_dict)

    @staticmethod
    def sys_set_notebooks_info(all_note_books_dict):
        if os.path.exists(BaiZeSys.PATH_FULL_NOTEBOOKS_JSON):
            shutil.copy(BaiZeSys.PATH_FULL_NOTEBOOKS_JSON,
                        BaiZeSys.PATH_FULL_NOTEBOOKS_JSON + str(datetime.today()) + ".backup")
        all_note_books_json_file = open(BaiZeSys.PATH_FULL_NOTEBOOKS_JSON, "w+")
        all_note_books_json_file.write(json.dumps(all_note_books_dict))
        all_note_books_json_file.close()

    @staticmethod
    def sys_get_notebooks_info():
        all_note_books_json_file = open(BaiZeSys.PATH_FULL_NOTEBOOKS_JSON, "r+")
        all_note_books_dict = json.loads(all_note_books_json_file.read())
        all_note_books_json_file.close()
        return all_note_books_dict

    @staticmethod
    def sys_get_notebooks_paths():
        return list(BaiZeSys.sys_get_notebooks_info().keys)

    @staticmethod
    def sys_check_notebooks_validation(notebooks_path_list):
        result_list = notebooks_path_list
        all_note_books_dict = BaiZeSys.sys_get_notebooks_info()
        modified_flag = False
        for notebook_path in notebooks_path_list:
            if notebook_path not in all_note_books_dict:
                BaiZeSys.sys_add_a_notebook(notebook_path, BaiZeSys.sys_get_new_notebook_info(notebook_path))
                modified_flag = True
            try:
                if not os.path.isdir(notebook_path):
                    raise InvalidNoteBookPathError
                elif not os.access(notebook_path, os.W_OK):
                    raise InvalidNoteBookPathError
            except InvalidNoteBookPathError:
                logging.error(
                    "\"%s\" no longer existed or have permission error, will remove from system" % notebook_path)
                all_note_books_dict.pop(notebook_path, None)
                result_list.remove(notebook_path)
                modified_flag = True
        if modified_flag:
            BaiZeSys.sys_set_notebooks_info(all_note_books_dict)
        return result_list

    @staticmethod
    def sys_get_processing_notebooks_list():
        processing_notebooks_list = []
        note_book_root = ""
        try:
            note_book_name_index = sys.argv.index("-g") + 1
            note_book_root = os.path.abspath(sys.argv[note_book_name_index])
            if os.path.isdir(note_book_root):
                if not os.access(note_book_root, os.W_OK):
                    raise PermissionError
                else:
                    processing_notebooks_list.append(note_book_root)
            else:
                raise WrongNoteBookPathError
        except IndexError:
            logging.critical("Process all note books stored in system")
            processing_notebooks_list = BaiZeSys.sys_get_notebooks_paths()
        except PermissionError:
            logging.error("Notebook folder \"%s\" permission error!" % note_book_root)
            if input(logging.critical("Do you want to process all notebooks stored in system?")).lower() in ["y",
                                                                                                             "yes"]:
                processing_notebooks_list = BaiZeSys.sys_get_notebooks_paths()
            else:
                return processing_notebooks_list
        except WrongNoteBookPathError:
            logging.error("Notebook folder \"%s\" path error!" % note_book_root)
            if input(logging.critical("Do you want to process all notebooks stored in system?")).lower() in ["y",
                                                                                                             "yes"]:
                processing_notebooks_list = BaiZeSys.sys_get_notebooks_paths()
            else:
                return processing_notebooks_list
        if len(processing_notebooks_list) == 1:
            new_note_book_path = processing_notebooks_list[0]
            if new_note_book_path not in BaiZeSys.sys_get_notebooks_info():
                BaiZeSys.sys_add_a_notebook(new_note_book_path, BaiZeSys.sys_get_new_notebook_info(new_note_book_path))
        return processing_notebooks_list

    @staticmethod
    def sys_get_new_notebook_info(note_book_path_full):
        while True:
            enter_author_string = "Please input notebook's author(s)'s name, " \
                                  "if multiple author please separate by comma \",\" : \n"
            confirm_author_string = "Is(Are) following your notebook's author(s) name(s)?(y/n)\n%s\n"
            author_raw = input(enter_author_string)
            author_list = author_raw.split(",")
            author_list = [x for x in author_list if x.strip()]
            if input(confirm_author_string % str(author_list)).lower() in ["yes", "y"]:
                break
        modification_time = [time.ctime(os.path.getmtime(note_book_path_full))]
        creation_time = time.ctime(os.path.getctime(note_book_path_full))
        if modification_time != creation_time:
            modification_time.insert(0, creation_time)
        note_book_dict = {"Author": author_list, "Note_Name": os.path.basename(note_book_path_full),
                          "Creation_time": creation_time, "Tag": []}
        return note_book_dict


class InvalidNoteBookPathError(Exception):
    """Notebook path is not correct"""


class WrongNoteBookPathError(Exception):
    """Input notebook path is not a dir"""
