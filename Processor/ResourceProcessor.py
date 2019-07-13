import time
from datetime import datetime
import json
import logging
import os
import shutil

from Processor.Constants.Paths import Paths
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
        result = list(ResourceProcessor.get_resource_notebooks_info())
        return result

    # Check processing notebook repositories permission
    # If invalid remove it from processing list and system's config
    # 检查即将处理的笔记仓库的权限
    # 如果非法将其从处理列表与系统设置中移除
    # @INPUT:
    # processing_list: List of notebook repositories going to be processed
    # processing_list: 即将处理的笔记仓库list
    # @Return:
    # processing_list: List of checked notebook repositories going to be processed
    # processing_list: 即将处理的笔记仓库list
    @staticmethod
    def check_resource_notebooks_validation(processing_list):
        result_list = processing_list
        all_note_books_dict = ResourceProcessor.get_resource_notebooks_info()
        modified_flag = False
        # 1. Check each notebook's permission
        for path in processing_list:
            # Check a notebook repository's config

            if not os.path.isdir(path) or not os.access(path, os.W_OK):
                error_info = "\"%s\" no longer existed or have permission error, will remove from system" % path
                logging.critical(error_info)
                all_note_books_dict.pop(path, None)
                result_list.remove(path)
                modified_flag = True
        # 2. When system config modified, update system config
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
