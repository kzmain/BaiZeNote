import copy
import json
import os
import re
import time
from pathlib import Path


class NotebookProcessor:
    PATH_REL_NOTEBOOK_JSON = ".notebook_config.json"
    PATH_REL_SECTION_JSON = ".section_info.json"

    SECTION_DICT_SECTION_NAME = "SECTION_NAME"
    SECTION_DICT_SECTION_LOCK = "SECTION_LOCK"
    SECTION_DICT_SECTION_HIDE = "SECTION_HIDE"
    SECTION_DICT_SECTION_TAGS = "SECTION_TAG"
    SECTION_DICT_SECTION_CREATION_TIME = "SECTION_CREATION_TIME"
    SECTION_DICT_SECTION_UPDATE_TIME = "SECTION_UPDATE_TIME"
    SECTION_DICT_SUB_SECTION_REL_PATH_DICT = "SUB_SECTION_REL_PATH_DICT"
    SECTION_DICT_NOTES_DICT = "NOTES_DICT"
    SECTION_DICT_REL_PATH = "REL_PATH"
    SECTION_DICT = {SECTION_DICT_REL_PATH: "",
                    SECTION_DICT_SECTION_NAME: "",
                    SECTION_DICT_SECTION_LOCK: False,
                    SECTION_DICT_SECTION_HIDE: False,
                    SECTION_DICT_SECTION_TAGS: [],
                    SECTION_DICT_SECTION_CREATION_TIME: "",
                    SECTION_DICT_SECTION_UPDATE_TIME: [],
                    SECTION_DICT_SUB_SECTION_REL_PATH_DICT: {},
                    SECTION_DICT_NOTES_DICT: {}
                    }
    NOTE_DICT_HTML_FILE_REL = "HTML_FILE_REL"
    NOTE_DICT_NOTE_FILE_TYPE = "NOTE_FILE_TYPE"
    NOTE_DICT_NOTE_NAME = "NOTE_FILE_NAME"
    NOTE_DICT_NOTE_FILE_PATH_REL = "NOTE_FILE_PATH"
    NOTE_DICT_NOTE_REFERENCES = "NOTE_REFERENCES"
    NOTE_DICT_NOTE_LOCK = "NOTE_LOCK"
    NOTE_DICT_NOTE_HIDE = "NOTE_HIDE"
    NOTE_DICT_NOTE_TAGS = "NOTE_TAG"
    NOTE_DICT_NOTE_CREATION_TIME = "NOTE_CREATION_TIME"
    NOTE_DICT_MODIFICATION_TIME = "NOTE_MODIFICATION_TIME"
    NOTE_DICT = {NOTE_DICT_NOTE_NAME: "",
                 NOTE_DICT_NOTE_FILE_PATH_REL: "",
                 NOTE_DICT_NOTE_FILE_TYPE: "",
                 NOTE_DICT_NOTE_REFERENCES: {},
                 NOTE_DICT_NOTE_LOCK: False,
                 NOTE_DICT_NOTE_HIDE: False,
                 NOTE_DICT_NOTE_TAGS: [],
                 NOTE_DICT_NOTE_CREATION_TIME: "",
                 NOTE_DICT_MODIFICATION_TIME: [], }
    PROCESS_FILE_TYPE_LIST = [".md"]

    @staticmethod
    def check_section_json(notebook_root):
        sections_dict = {}
        for root, dirs, files in os.walk(notebook_root):
            section_json_path_full = os.path.join(root, NotebookProcessor.PATH_REL_SECTION_JSON)
            if not os.path.exists(section_json_path_full):
                current_section_dict = NotebookProcessor.__initial_section_json(root, notebook_root)
            else:
                file = open(section_json_path_full, "r")
                try:
                    section_dict = json.loads(file.read())
                    current_section_dict = NotebookProcessor.__update_section_json(section_dict, root, notebook_root)
                except json.decoder.JSONDecodeError:
                    # 如果无法load 删除 rm 新
                    os.remove(section_json_path_full)
                    current_section_dict = NotebookProcessor.__initial_section_json(root, notebook_root)
                file.close()
            sections_dict[current_section_dict[NotebookProcessor.SECTION_DICT_REL_PATH]] = current_section_dict
        return sections_dict

    @staticmethod
    def __initial_section_json(section_path, notebook_root):
        file_dir_list = os.listdir(section_path)
        dir_list = []
        file_list = []
        # 1. 将当前目录的子目录和子文件分开，将目录储存于dir_list，将文件储存于file_list
        for file_dir in file_dir_list:
            file_dir_path = os.path.join(section_path, file_dir)
            if os.path.isdir(file_dir_path):
                dir_list.append(os.path.relpath(file_dir_path, notebook_root))
            elif os.path.isfile(file_dir_path) and (
                    Path(file_dir_path).suffix.lower() in NotebookProcessor.PROCESS_FILE_TYPE_LIST):
                file_list.append(os.path.relpath(file_dir_path, notebook_root))
        # 2. 处理基本信息，有：
        # 目录相对路径
        # 目录section名称
        # 目录创建时间
        # 目录最后更新时间
        section_dict = copy.deepcopy(NotebookProcessor.SECTION_DICT)
        section_dict[NotebookProcessor.SECTION_DICT_REL_PATH] = os.path.relpath(section_path, notebook_root)
        section_dict[NotebookProcessor.SECTION_DICT_SECTION_NAME] = os.path.basename(section_path)
        section_dict[NotebookProcessor.SECTION_DICT_SECTION_CREATION_TIME] = \
            time.ctime(os.path.getctime(section_path))
        section_dict[NotebookProcessor.SECTION_DICT_SECTION_UPDATE_TIME] = [
            time.ctime(os.path.getmtime(section_path))]
        # 3. 处理子目录相关信息，有：
        # 子目录与笔记本根目录对应的相对路径
        dir_id = 0
        for dir_path in dir_list:
            file_path = os.path.join(notebook_root, dir_path)
            section_dict[NotebookProcessor.SECTION_DICT_SUB_SECTION_REL_PATH_DICT][dir_id] = \
                os.path.relpath(file_path, notebook_root)
            dir_id += 1
        # 4. 处理子文件相关信息，有：
        # 子文件与笔记本根目录对应的相对路径
        # 子文件文件类型
        # 子文件名称（含后缀）
        # 子文件创建时间
        # 子文件最后更改时间
        file_id = 0
        for file_path in file_list:
            file_path = os.path.join(notebook_root, file_path)
            file_dict = copy.deepcopy(NotebookProcessor.NOTE_DICT)
            file_dict[NotebookProcessor.NOTE_DICT_NOTE_FILE_PATH_REL] = \
                os.path.relpath(file_path, notebook_root)
            file_dict[NotebookProcessor.NOTE_DICT_NOTE_FILE_TYPE] = Path(file_path).suffix.lower()
            file_dict[NotebookProcessor.NOTE_DICT_NOTE_NAME] = \
                re.sub("%s$" % file_dict[NotebookProcessor.NOTE_DICT_NOTE_FILE_TYPE], "", os.path.basename(file_path))
            file_dict[NotebookProcessor.NOTE_DICT_NOTE_CREATION_TIME] = time.ctime(os.path.getctime(file_path))
            file_dict[NotebookProcessor.NOTE_DICT_MODIFICATION_TIME] = [time.ctime(os.path.getctime(file_path))]
            section_dict[NotebookProcessor.SECTION_DICT_NOTES_DICT]["%s" % file_id] = file_dict
            file_id += 1
        # 5. 写入section信息
        section_json_file = open(os.path.join(section_path, NotebookProcessor.PATH_REL_SECTION_JSON), "w+")
        section_json_file.write(json.dumps(section_dict))
        section_json_file.close()
        return section_dict

    @staticmethod
    def __update_section_json(ori_section_dict, section_path_full, notebook_root):
        dirs_dict = ori_section_dict[NotebookProcessor.SECTION_DICT_SUB_SECTION_REL_PATH_DICT]
        files_dict = ori_section_dict[NotebookProcessor.SECTION_DICT_NOTES_DICT]

        new_dir_file_list = NotebookProcessor.__get_dir_file_list(section_path_full, notebook_root)

        modified_flag = False
        # 检查基本信息
        ori_section_dict[NotebookProcessor.SECTION_DICT_SECTION_UPDATE_TIME].append(time.ctime(time.time()))
        ori_path = ori_section_dict[NotebookProcessor.SECTION_DICT_REL_PATH]
        cur_path = os.path.relpath(section_path_full, notebook_root)
        if ori_path != cur_path:
            modified_flag = True
            ori_section_dict[NotebookProcessor.SECTION_DICT_REL_PATH] = cur_path
        # ---------------检查sub-section增减， ！！！要加入modified time！
        ori_dir_list = list(dirs_dict.values())
        cur_dir_list = new_dir_file_list[0]
        if ori_dir_list != cur_dir_list:
            modified_flag = True
            del_folders_list = list(set(ori_dir_list) - set(cur_dir_list))
            add_folders_list = list(set(cur_dir_list) - set(ori_dir_list))
            if len(del_folders_list) > 0:
                for del_folder in del_folders_list:
                    del_dir = dirs_dict.pop(str(ori_dir_list.index(del_folder)))
                    print("%s folder removed." % str(os.path.join(section_path_full, del_dir)))
            if len(add_folders_list) > 0:
                for add_folder in add_folders_list:
                    keys_list = list(dirs_dict.keys())
                    if len(keys_list) == 0:
                        new_key = "%s" % 0
                    else:
                        new_key = "%s" % (int(keys_list[len(keys_list) - 1]) + 1)
                    dirs_dict[new_key] = add_folder
                    print("%s folder added." % str(os.path.join(section_path_full, add_folder)))

        # -----------------检查sub-notes增减，

        ori_notes_dict = {}
        for note_key, note_dict in files_dict.items():
            sub_note_path = note_dict[NotebookProcessor.NOTE_DICT_NOTE_FILE_PATH_REL]
            ori_notes_dict[sub_note_path] = note_key
        cur_notes_list = new_dir_file_list[1]
        ori_notes_list = list(ori_notes_dict.keys())
        if ori_notes_list != cur_notes_list:
            modified_flag = True
            del_notes_list = list(set(ori_notes_list) - set(cur_notes_list))
            add_notes_list = list(set(cur_notes_list) - set(ori_notes_list))
            # 删除
            if len(del_notes_list) > 0:
                for del_note_path in del_notes_list:
                    note_index = ori_notes_dict[del_note_path]
                    del_file = files_dict[note_index][NotebookProcessor.NOTE_DICT_NOTE_FILE_PATH_REL]
                    files_dict.pop(note_index)
                    print("%s note removed." % str(os.path.join(section_path_full, del_file)))
            # 增加
            if len(add_notes_list) > 0:
                for note_file_name in add_notes_list:
                    # !!!!测试
                    note_file_name = os.path.join(notebook_root, note_file_name)
                    note_file_path_full = note_file_name
                    note_file_path_rel = os.path.relpath(note_file_path_full, notebook_root)
                    note_suffix = Path(note_file_name).suffix.lower()
                    note_name = str(os.path.basename(note_file_name).split(".")[0])
                    note_ctime = time.ctime(os.path.getctime(note_file_name))
                    note_mtime = time.ctime(os.path.getmtime(note_file_name))
                    # values_list = list(files_dict.values())
                    if len(files_dict) == 0:
                        new_key = "%s" % 0
                    else:
                        last_key = int(list(files_dict.keys())[-1]) + 1
                        new_key = "%s" % last_key
                    new_note_dict = copy.deepcopy(NotebookProcessor.NOTE_DICT)
                    new_note_dict[NotebookProcessor.NOTE_DICT_NOTE_FILE_PATH_REL] = note_file_path_rel
                    new_note_dict[NotebookProcessor.NOTE_DICT_NOTE_FILE_TYPE] = note_suffix
                    new_note_dict[NotebookProcessor.NOTE_DICT_NOTE_NAME] = note_name
                    new_note_dict[NotebookProcessor.NOTE_DICT_NOTE_CREATION_TIME] = note_ctime
                    new_note_dict[NotebookProcessor.NOTE_DICT_MODIFICATION_TIME] = [note_mtime]
                    files_dict["%s" % new_key] = new_note_dict
                    print("%s note added." % str(os.path.join(notebook_root, note_file_name)))
                count = 0
                for key, values in files_dict.items():
                    files_dict[str(count)] = values
                    count += 1
        # -----------------是否更改过。md文件
        for note_key, note_dict in files_dict.items():
            old_note_path_full = os.path.join(notebook_root, note_dict[NotebookProcessor.NOTE_DICT_NOTE_FILE_PATH_REL])
            new_note_path_full = os.path.join(notebook_root, files_dict[note_key][NotebookProcessor.NOTE_DICT_NOTE_FILE_PATH_REL])
            rel_path = os.path.relpath(new_note_path_full, notebook_root)
            if old_note_path_full != new_note_path_full:
                modified_flag = True
                files_dict[note_key][NotebookProcessor.NOTE_DICT_NOTE_FILE_PATH_REL] = rel_path

            new_mtime = time.ctime(os.path.getctime(old_note_path_full))
            ori_mtime = note_dict[NotebookProcessor.NOTE_DICT_MODIFICATION_TIME]

            if new_mtime not in ori_mtime:
                modified_flag = True
                files_dict[note_key][NotebookProcessor.NOTE_DICT_MODIFICATION_TIME].append(new_mtime)
        if modified_flag:
            section_json_path_full = os.path.join(section_path_full, NotebookProcessor.PATH_REL_SECTION_JSON)
            section_json_file = open(section_json_path_full, "w+")
            section_json_file.write(json.dumps(ori_section_dict))
            section_json_file.close()
        return ori_section_dict

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
                    Path(file_dir_path).suffix.lower() in NotebookProcessor.PROCESS_FILE_TYPE_LIST):
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
