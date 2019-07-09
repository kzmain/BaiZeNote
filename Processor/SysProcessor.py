import json
import logging
import os
import sys

from Processor.Constants import Paths
from Processor.Exception.Exceptions import WrongNoteBookPathError
from Processor.ResourceProcessor import ResourceProcessor


class SysProcessor:
    # NOTEBOOKS_REPO_LOCATION_KEY = "NOTE_BOOKS_REPO_PATH_FULL"

    check_configs = {
        Paths.PATH_FULL_NOTEBOOKS_RES_LOCATION_JSON: {},
        Paths.PATH_FULL_NOTEBOOKS_THEME_JSON: {"current": "default", "default": "default"}
    }

    @staticmethod
    def configs_check():
        for path, default_value in SysProcessor.check_configs.items():
            if not os.path.exists(path):
                all_note_books_json = open(path, "w+")
                all_note_books_json.write(json.dumps(default_value))
                all_note_books_json.close()
        if not os.path.exists(Paths.PATH_FULL_NOTEBOOKS_DEST_LOCATION_JSON):
            return False
        else:
            return True

    @staticmethod
    def get_processing_notebooks_list():
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
            processing_notebooks_list = ResourceProcessor.get_resource_notebooks_paths()
        except PermissionError:
            logging.error("Notebook folder \"%s\" permission error!" % note_book_root)
            logging.critical("Do you want to process all notebooks stored in system?")
            if input().lower() in ["y", "yes"]:
                processing_notebooks_list = ResourceProcessor.get_resource_notebooks_paths()
            else:
                return processing_notebooks_list
        except WrongNoteBookPathError:
            logging.error("Notebook folder \"%s\" path error!" % note_book_root)
            logging.critical("Do you want to process all notebooks stored in system?")
            if input().lower() in ["y", "yes"]:
                processing_notebooks_list = ResourceProcessor.get_resource_notebooks_paths()
            else:
                return processing_notebooks_list
        if len(processing_notebooks_list) == 1:
            new_note_book_path = processing_notebooks_list[0]
            if new_note_book_path not in ResourceProcessor.get_resource_notebooks_info():
                new_note_book_info_dict = ResourceProcessor.get_new_notebook_info(new_note_book_path)
                ResourceProcessor.add_resource_notebook(new_note_book_path, new_note_book_info_dict)
        return processing_notebooks_list
