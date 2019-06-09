import json
import os
import shutil
import time
from pathlib import Path


class Source:
    SOURCE_PATH_REL_NOTEBOOK_JSON = ".notebook_config.json"
    SOURCE_PATH_REL_SECTION_JSON = ".section_info.json"

    SOURCE_SECTION_DICT_SECTION_NAME = "SECTION_NAME"
    SOURCE_SECTION_DICT_SECTION_LOCK = "SECTION_LOCK"
    SOURCE_SECTION_DICT_SECTION_HIDE = "SECTION_HIDE"
    SOURCE_SECTION_DICT_SECTION_TAGS = "SECTION_TAG"
    SOURCE_SECTION_DICT_SECTION_CREATION_TIME = "SECTION_CREATION_TIME"
    SOURCE_SECTION_DICT_SECTION_MODIFICATION_TIME = "SECTION_MODIFICATION_TIME"
    SOURCE_SECTION_DICT_SUB_SECTION_LIST = "SUB_SECTION_LIST"
    SOURCE_SECTION_DICT_NOTES_DICT = "NOTES_DICT"
    SOURCE_SECTION_DICT_REL_PATH = "REL_PATH"
    SOURCE_SECTION_DICT = {SOURCE_SECTION_DICT_REL_PATH: "",
                           SOURCE_SECTION_DICT_SECTION_NAME: "",
                           SOURCE_SECTION_DICT_SECTION_LOCK: False,
                           SOURCE_SECTION_DICT_SECTION_HIDE: False,
                           SOURCE_SECTION_DICT_SECTION_TAGS: [],
                           SOURCE_SECTION_DICT_SECTION_CREATION_TIME: "",
                           SOURCE_SECTION_DICT_SECTION_MODIFICATION_TIME: [],
                           SOURCE_SECTION_DICT_SUB_SECTION_LIST: [],
                           SOURCE_SECTION_DICT_NOTES_DICT: {}
                           }
    SOURCE_SUB_NOTE_DICT_NOTE_FILE_TYPE = "NOTE_FILE_TYPE"
    _SOURCE_SUB_NOTE_DICT_NOTE_FILE_NAME = "NOTE_FILE_NAME"
    _SOURCE_SUB_NOTE_DICT_NOTE_FILE_PATH_REL = "NOTE_FILE_PATH"
    SOURCE_SUB_NOTE_DICT_NOTE_REFERENCES = "NOTE_REFERENCES"
    SOURCE_SUB_NOTE_DICT_NOTE_LOCK = "NOTE_LOCK"
    SOURCE_SUB_NOTE_DICT_NOTE_HIDE = "NOTE_HIDE"
    SOURCE_SUB_NOTE_DICT_NOTE_TAGS = "NOTE_TAG"
    SOURCE_SUB_NOTE_DICT_NOTE_CREATION_TIME = "NOTE_CREATION_TIME"
    SOURCE_SUB_NOTE_DICT_SECTION_MODIFICATION_TIME = "SECTION_MODIFICATION_TIME"
    SOURCE_SUB_NOTE_DICT = {SOURCE_SUB_NOTE_DICT_NOTE_FILE_TYPE: "",
                            SOURCE_SUB_NOTE_DICT_NOTE_REFERENCES: {},
                            SOURCE_SUB_NOTE_DICT_NOTE_LOCK: False,
                            SOURCE_SUB_NOTE_DICT_NOTE_HIDE: False,
                            SOURCE_SUB_NOTE_DICT_NOTE_TAGS: [],
                            SOURCE_SUB_NOTE_DICT_NOTE_CREATION_TIME: "",
                            SOURCE_SUB_NOTE_DICT_SECTION_MODIFICATION_TIME: [], }
    SOURCE_PROCESS_FILE_TYPE_LIST = [".md"]

    @staticmethod
    def source_check_section_json(notebook_root):
        for root, dirs, files in os.walk(notebook_root):
            # 如果无法load 删除 rm 新 ！！！！！
            Source.initial_section_json(root, notebook_root)

    @staticmethod
    def initial_section_json(section_path, notebook_root):
        file_dir_list = os.listdir(section_path)
        dir_list = []
        file_list = []
        for file_dir in file_dir_list:
            file_dir_path = os.path.join(section_path, file_dir)
            if os.path.isdir(file_dir_path):
                dir_list.append(os.path.relpath(file_dir_path, notebook_root))
            elif os.path.isfile(file_dir_path) and (
                    Path(file_dir_path).suffix.lower() in Source.SOURCE_PROCESS_FILE_TYPE_LIST):
                file_list.append(os.path.relpath(file_dir_path, notebook_root))
        section_dict = Source.SOURCE_SECTION_DICT
        section_dict[Source.SOURCE_SECTION_DICT_REL_PATH] = os.path.relpath(section_path, notebook_root)
        section_dict[Source.SOURCE_SECTION_DICT_SECTION_NAME] = os.path.basename(section_path)
        section_dict[Source.SOURCE_SECTION_DICT_SECTION_CREATION_TIME] = time.ctime(os.path.getctime(section_path))
        section_dict[Source.SOURCE_SECTION_DICT_SECTION_MODIFICATION_TIME] = [
            time.ctime(os.path.getmtime(section_path))]
        section_dict[Source.SOURCE_SECTION_DICT_SUB_SECTION_LIST] = dir_list

        file_id = 0
        for file_path in file_list:
            file_path = os.path.join(notebook_root, file_path)
            file_dict = Source.SOURCE_SUB_NOTE_DICT
            file_dict[Source._SOURCE_SUB_NOTE_DICT_NOTE_FILE_NAME] = os.path.basename(file_path)
            file_dict[Source._SOURCE_SUB_NOTE_DICT_NOTE_FILE_PATH_REL] = os.path.relpath(file_path, notebook_root)
            file_dict[Source.SOURCE_SUB_NOTE_DICT_NOTE_FILE_TYPE] = Path(file_path).suffix.lower()
            file_dict[Source.SOURCE_SUB_NOTE_DICT_NOTE_CREATION_TIME] = time.ctime(os.path.getctime(file_path))
            file_dict[Source.SOURCE_SUB_NOTE_DICT_SECTION_MODIFICATION_TIME] = [time.ctime(os.path.getctime(file_path))]
            section_dict[Source.SOURCE_SECTION_DICT_NOTES_DICT]["file%s" % file_id] = file_dict
            file_id += 1
        section_json_file = open(os.path.join(section_path, Source.SOURCE_PATH_REL_SECTION_JSON), "w+")
        section_json_file.write(json.dumps(section_dict))
        section_json_file.close()

#
# def update_notebook_json(note_book_root_location):
#     # c_datetime = datetime.datetime.now()
#     # current_date = "%s-%s-%s" % (c_datetime.year, c_datetime.month, c_datetime.day)
#     # current_time = "%s:%s:%s:%s" % (c_datetime.hour, c_datetime.minute, c_datetime.second, c_datetime.microsecond)
#     # note_name = os.path.basename(note_book_root_location)
#     # 情况 2 如果 .notebook.json 存在则添加最新更改时间
#     # Circumstance 2 if .notebook.json exists add current update time
#     # note_book_config_json_full_path = os.path.join(note_book_root_location, Source.SOURCE_PATH_REL_NOTEBOOK_JSON)
#     notebooks_config_full_path = os.path.join(System.PATH_FULL_SYS, System.PATH_RELA_NOTEBOOKS_JSON)
#     notebooks_config_file = open(notebooks_config_full_path, "r")
#     notebooks_config_dict = json.loads(notebooks_config_file.read())
#     if note_book_root_location in notebooks_config_dict:
#         # ！！！！！！！要只用r+覆盖
#         note_book_json_file = open(note_book_config_json_full_path, "r")
#         note_book_dict = json.loads(note_book_json_file.read())
#         note_book_json_file.close()
#         note_book_json_file = open(note_book_config_json_full_path, "w+")
#         new_ctime = time.ctime(os.path.getmtime(note_book_config_json_full_path))
#         if new_ctime not in note_book_dict["Modification_Time"]:
#             note_book_dict["Modification_Time"].append(new_ctime)
#             note_book_json_file.write(json.dumps(note_book_dict))
#         note_book_json_file.close()
#     # 情况 2 如果 .notebook.json 不存在,则初始化写入信息到 .notebook.json
#     # Circumstance 2 if .notebook.json does NOT exist, write initial info to .notebook.json
#     else:
#         while True:
#             enter_author_string = "Please input notebook name, if multiple author please separate by comma \",\" : \n"
#             confirm_author_string = "Is(Are) following your notebook's author(s) name(s)?(y/n)\n%s\n"
#             author_raw = input(enter_author_string)
#             author_list = author_raw.split(",")
#             author_list = [x for x in author_list if x.strip()]
#             if input(confirm_author_string % str(author_list)).lower() in ["yes", "y"]:
#                 break
#         note_book_dict = {"Author": author_list, "Note_Name": os.path.basename(note_book_root_location),
#                           "Creation_time": time.ctime(os.path.getctime(note_book_config_json_full_path)),
#                           "Modification_Time": [time.ctime(os.path.getmtime(note_book_config_json_full_path))]
#                           }
#     System.sys_add_a_note_book(note_book_root_location, note_book_dict)
#     return note_book_dict
