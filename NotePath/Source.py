import copy
import json
import os
import re
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
    SOURCE_SECTION_DICT_SUB_SECTION_REL_PATH_DICT = "SUB_SECTION_REL_PATH_DICT"
    SOURCE_SECTION_DICT_NOTES_DICT = "NOTES_DICT"
    SOURCE_SECTION_DICT_REL_PATH = "REL_PATH"
    SOURCE_SECTION_DICT = {SOURCE_SECTION_DICT_REL_PATH: "",
                           SOURCE_SECTION_DICT_SECTION_NAME: "",
                           SOURCE_SECTION_DICT_SECTION_LOCK: False,
                           SOURCE_SECTION_DICT_SECTION_HIDE: False,
                           SOURCE_SECTION_DICT_SECTION_TAGS: [],
                           SOURCE_SECTION_DICT_SECTION_CREATION_TIME: "",
                           SOURCE_SECTION_DICT_SECTION_MODIFICATION_TIME: [],
                           SOURCE_SECTION_DICT_SUB_SECTION_REL_PATH_DICT: {},
                           SOURCE_SECTION_DICT_NOTES_DICT: {}
                           }
    SOURCE_SUB_NOTE_DICT_HTML_FILE_REL = "HTML_FILE_REL"
    SOURCE_SUB_NOTE_DICT_NOTE_FILE_TYPE = "NOTE_FILE_TYPE"
    SOURCE_SUB_NOTE_DICT_NOTE_NAME = "NOTE_FILE_NAME"
    SOURCE_SUB_NOTE_DICT_NOTE_FILE_PATH_REL = "NOTE_FILE_PATH"
    SOURCE_SUB_NOTE_DICT_NOTE_REFERENCES = "NOTE_REFERENCES"
    SOURCE_SUB_NOTE_DICT_NOTE_LOCK = "NOTE_LOCK"
    SOURCE_SUB_NOTE_DICT_NOTE_HIDE = "NOTE_HIDE"
    SOURCE_SUB_NOTE_DICT_NOTE_TAGS = "NOTE_TAG"
    SOURCE_SUB_NOTE_DICT_NOTE_CREATION_TIME = "NOTE_CREATION_TIME"
    SOURCE_SUB_NOTE_DICT_MODIFICATION_TIME = "NOTE_MODIFICATION_TIME"
    SOURCE_SUB_NOTE_DICT = {SOURCE_SUB_NOTE_DICT_NOTE_NAME: "",
                            SOURCE_SUB_NOTE_DICT_NOTE_FILE_PATH_REL: "",
                            SOURCE_SUB_NOTE_DICT_NOTE_FILE_TYPE: "",
                            SOURCE_SUB_NOTE_DICT_NOTE_REFERENCES: {},
                            SOURCE_SUB_NOTE_DICT_NOTE_LOCK: False,
                            SOURCE_SUB_NOTE_DICT_NOTE_HIDE: False,
                            SOURCE_SUB_NOTE_DICT_NOTE_TAGS: [],
                            SOURCE_SUB_NOTE_DICT_NOTE_CREATION_TIME: "",
                            SOURCE_SUB_NOTE_DICT_MODIFICATION_TIME: [], }
    SOURCE_PROCESS_FILE_TYPE_LIST = [".md"]

    @staticmethod
    def source_check_section_json(notebook_root):
        sections_dict_list = {}
        for root, dirs, files in os.walk(notebook_root):
            section_json_path_full = os.path.join(root, Source.SOURCE_PATH_REL_SECTION_JSON)
            if not os.path.exists(section_json_path_full):
                current_section_dict = Source.initial_section_json(root, notebook_root)
            else:
                file = open(section_json_path_full, "r")
                try:
                    section_dict = json.loads(file.read())
                    current_section_dict = Source.update_section_json(section_dict, root, notebook_root)
                except json.decoder.JSONDecodeError:
                    # 如果无法load 删除 rm 新
                    os.remove(section_json_path_full)
                    current_section_dict = Source.initial_section_json(root, notebook_root)
                file.close()
            sections_dict_list[current_section_dict[Source.SOURCE_SECTION_DICT_REL_PATH]] = current_section_dict
        return sections_dict_list

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
        section_dict = copy.deepcopy(Source.SOURCE_SECTION_DICT)
        section_dict[Source.SOURCE_SECTION_DICT_REL_PATH] = os.path.relpath(section_path, notebook_root)
        section_dict[Source.SOURCE_SECTION_DICT_SECTION_NAME] = os.path.basename(section_path)
        section_dict[Source.SOURCE_SECTION_DICT_SECTION_CREATION_TIME] = time.ctime(os.path.getctime(section_path))
        section_dict[Source.SOURCE_SECTION_DICT_SECTION_MODIFICATION_TIME] = [
            time.ctime(os.path.getmtime(section_path))]
        dir_id = 0
        for dir_path in dir_list:
            file_path = os.path.join(notebook_root, dir_path)
            section_dict[Source.SOURCE_SECTION_DICT_SUB_SECTION_REL_PATH_DICT][dir_id] = os.path.relpath(file_path,
                                                                                                         notebook_root)
            dir_id += 1
        file_id = 0
        for file_path in file_list:
            file_path = os.path.join(notebook_root, file_path)
            file_dict = copy.deepcopy(Source.SOURCE_SUB_NOTE_DICT)
            file_dict[Source.SOURCE_SUB_NOTE_DICT_NOTE_FILE_PATH_REL] = os.path.relpath(file_path, notebook_root)
            file_dict[Source.SOURCE_SUB_NOTE_DICT_NOTE_FILE_TYPE] = Path(file_path).suffix.lower()

            file_dict[Source.SOURCE_SUB_NOTE_DICT_NOTE_NAME] = \
                re.sub("%s$" % file_dict[Source.SOURCE_SUB_NOTE_DICT_NOTE_FILE_TYPE], "", os.path.basename(file_path))
            file_dict[Source.SOURCE_SUB_NOTE_DICT_NOTE_CREATION_TIME] = time.ctime(os.path.getctime(file_path))
            file_dict[Source.SOURCE_SUB_NOTE_DICT_MODIFICATION_TIME] = [time.ctime(os.path.getctime(file_path))]
            section_dict[Source.SOURCE_SECTION_DICT_NOTES_DICT]["%s" % file_id] = file_dict
            file_id += 1
        section_json_file = open(os.path.join(section_path, Source.SOURCE_PATH_REL_SECTION_JSON), "w+")
        section_json_file.write(json.dumps(section_dict))
        section_json_file.close()
        return section_dict

    @staticmethod
    def update_section_json(original_section_dict, section_path, notebook_root):

        original_sub_sections_dict = original_section_dict[Source.SOURCE_SECTION_DICT_SUB_SECTION_REL_PATH_DICT]
        original_sub_notes_dict = original_section_dict[Source.SOURCE_SECTION_DICT_NOTES_DICT]
        dir_file_list = Source.__get_dir_file_list(section_path, notebook_root)

        original_sub_sections_list = list(original_sub_sections_dict.values())
        current_sub_sections_list = dir_file_list[0]
        modified_flag = False
        # ---------------检查sub-section增减， ！！！要加入modifed time！
        if original_sub_sections_list != current_sub_sections_list:
            modified_flag = True
            del_folders_list = list(set(original_sub_sections_list) - set(current_sub_sections_list))
            add_folders_list = list(set(current_sub_sections_list) - set(original_sub_sections_list))
            if len(del_folders_list) > 0:
                for del_folder in del_folders_list:
                    original_sub_sections_dict.pop(str(original_sub_sections_list.index(del_folder)))
            if len(add_folders_list) > 0:
                for add_folder in add_folders_list:
                    keys_list = list(original_sub_sections_dict.keys())
                    if len(keys_list) == 0:
                        new_key = "%s" % 0
                    else:
                        new_key = "%s" % (int(keys_list[len(keys_list) - 1]) + 1)
                    original_sub_sections_dict[new_key] = add_folder

        current_sub_notes_list = dir_file_list[1]
        orig_sub_notes_path_key_pair_dict = {}
        for sub_note_key, sub_note_dict in original_sub_notes_dict.items():
            sub_note_path = sub_note_dict[Source.SOURCE_SUB_NOTE_DICT_NOTE_FILE_PATH_REL]
            orig_sub_notes_path_key_pair_dict[sub_note_path] = sub_note_key
        # -----------------检查sub-notes增减，
        if list(orig_sub_notes_path_key_pair_dict.keys()) != current_sub_notes_list:
            modified_flag = True
            del_notes_list = list(set(list(orig_sub_notes_path_key_pair_dict.keys())) - set(current_sub_notes_list))
            add_notes_list = list(set(current_sub_notes_list) - set(list(orig_sub_notes_path_key_pair_dict.keys())))
            # 删除
            if len(del_notes_list) > 0:
                for del_note_path in del_notes_list:
                    original_sub_notes_dict.pop(orig_sub_notes_path_key_pair_dict[del_note_path])
            # 增加
            if len(add_notes_list) > 0:
                for add_note_path in add_notes_list:
                    add_note_path = os.path.join(notebook_root, add_note_path)
                    values_list = list(orig_sub_notes_path_key_pair_dict.values())
                    if len(values_list) == 0:
                        new_key = "%s" % 0
                    else:
                        new_key = "%s" % (int(values_list[len(values_list) - 1]) + 1)
                    new_note_dict = copy.deepcopy(Source.SOURCE_SUB_NOTE_DICT)
                    new_note_dict[Source.SOURCE_SUB_NOTE_DICT_NOTE_FILE_PATH_REL] = os.path.relpath(add_note_path,
                                                                                                    notebook_root)
                    new_note_dict[Source.SOURCE_SUB_NOTE_DICT_NOTE_FILE_TYPE] = Path(add_note_path).suffix.lower()
                    new_note_dict[Source.SOURCE_SUB_NOTE_DICT_NOTE_NAME] = str(
                        os.path.basename(add_note_path).split(".")[0])
                    new_note_dict[Source.SOURCE_SUB_NOTE_DICT_NOTE_CREATION_TIME] = time.ctime(
                        os.path.getctime(add_note_path))
                    new_note_dict[Source.SOURCE_SUB_NOTE_DICT_MODIFICATION_TIME] = [
                        time.ctime(os.path.getctime(add_note_path))]
                    original_sub_notes_dict["%s" % new_key] = new_note_dict
        # 是否更改过。md文件
        for sub_note_key, sub_note_dict in original_sub_notes_dict.items():
            note_path_full = os.path.join(notebook_root, sub_note_dict[Source.SOURCE_SUB_NOTE_DICT_NOTE_FILE_PATH_REL])
            latest_modification_time = time.ctime(os.path.getctime(note_path_full))

            original_modification_time_list = sub_note_dict[Source.SOURCE_SUB_NOTE_DICT_MODIFICATION_TIME]
            if latest_modification_time not in original_modification_time_list:
                modified_flag = True
                original_sub_notes_dict[sub_note_key][Source.SOURCE_SUB_NOTE_DICT_MODIFICATION_TIME].append(
                    latest_modification_time)
        if modified_flag:
            section_json_path_full = os.path.join(section_path, Source.SOURCE_PATH_REL_SECTION_JSON)
            section_json_file = open(section_json_path_full, "w+")
            section_json_file.write(json.dumps(original_section_dict))
            section_json_file.close()
        return original_section_dict

    @staticmethod
    def __get_dir_file_list(section_path, notebook_root):
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
        return dir_list, file_list
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
