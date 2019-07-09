import time
from datetime import datetime
import json
import logging
import os
import shutil

from Processor.Constants import Paths
from Processor.Exception.Exceptions import InvalidNoteBookPathError


class ResourceProcessor:

    @staticmethod
    def add_resource_notebook(note_book_path, note_book_info_dict):
        all_note_books_dict = ResourceProcessor.get_resource_notebooks_info()
        if note_book_path not in all_note_books_dict:
            all_note_books_dict[note_book_path] = note_book_info_dict
            ResourceProcessor.set_resource_notebook_info(all_note_books_dict)

    @staticmethod
    def set_resource_notebook_info(all_note_books_dict):
        if os.path.exists(Paths.PATH_FULL_NOTEBOOKS_RES_LOCATION_JSON):
            old_file_name = Paths.PATH_FULL_NOTEBOOKS_RES_LOCATION_JSON
            new_file_name = "%s%s%s" % (Paths.PATH_FULL_NOTEBOOKS_RES_LOCATION_JSON, str(datetime.today()), ".backup")
            shutil.copy(old_file_name, new_file_name)
        all_note_books_json_file = open(Paths.PATH_FULL_NOTEBOOKS_RES_LOCATION_JSON, "w+")
        all_note_books_json_file.write(json.dumps(all_note_books_dict))
        all_note_books_json_file.close()

    @staticmethod
    def get_resource_notebooks_info():
        all_note_books_json_file = open(Paths.PATH_FULL_NOTEBOOKS_RES_LOCATION_JSON, "r+")
        all_note_books_dict = json.loads(all_note_books_json_file.read())
        all_note_books_json_file.close()
        return all_note_books_dict

    @staticmethod
    def get_resource_notebooks_paths():
        return list(ResourceProcessor.get_resource_notebooks_info().keys)

    @staticmethod
    def check_resource_notebooks_validation(notebooks_path_list):
        result_list = notebooks_path_list
        all_note_books_dict = ResourceProcessor.get_resource_notebooks_info()
        modified_flag = False
        for notebook_path in notebooks_path_list:
            if notebook_path not in all_note_books_dict:
                new_note_info_dict = ResourceProcessor.get_new_notebook_info(notebook_path)
                ResourceProcessor.add_resource_notebook(notebook_path, new_note_info_dict)
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
            ResourceProcessor.set_resource_notebook_info(all_note_books_dict)
        return result_list

    @staticmethod
    def get_new_notebook_info(note_book_path_full):
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
