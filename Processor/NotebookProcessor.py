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

    # 📕 核心功能
    # 建立/更新指定的的笔记本section和笔记的信息
    # ⬇️ 参数
    # notebook_root: 笔记本的根目录（即笔记本的源仓库所在位置）
    # ⬆️ 返回值
    # sections_dict: All sections and their containing notes info
    # 🎯️ 应用
    # NotebookProcessor.check_section_json()
    # ------------------------------------------------------------------------------------------------------------------
    # 📕 Core function
    # Setup/Update the specific notebook's section and note info
    # ⬇️ Parameter:
    # notebook_root: Notebook's root location (resource repository location)
    # ⬆️ Return
    # sections_dict: 所有section的及其包含的note的信息
    # 🎯Usage:
    # NotebookProcessor.check_section_json()
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
                    # 如果无法load 删除 rm 更新
                    os.remove(section_json_path_full)
                    current_section_dict = NotebookProcessor.__initial_section_json(root, notebook_root)
                file.close()
            sections_dict[current_section_dict[NotebookProcessor.SECTION_DICT_REL_PATH]] = current_section_dict
        return sections_dict

    # 📕 核心功能
    # 建立指定的的笔记本section和笔记的信息
    # ⬇️ 参数
    # section_path: 系统中section的绝对路径
    # notebook_root: 笔记本的根目录（即笔记本的源仓库所在位置）
    # ⬆️ 返回值
    # section_dict: 当前section的信息字典
    # 🎯️ 应用
    # NotebookProcessor.check_section_json()
    # ------------------------------------------------------------------------------------------------------------------
    # 📕 Core function
    # Setup the specific notebook's section and note info
    # ⬇️ Parameter:
    # section_path: Section full path in system
    # notebook_root: Notebook's root location (resource repository location)
    # ⬆️ Return
    # section_dict: current section's info dict
    # 🎯Usage:
    # NotebookProcessor.check_section_json()
    @staticmethod
    def __initial_section_json(section_path, notebook_root):
        file_dir_list = os.listdir(section_path)
        dir_list = []
        file_list = []
        # 1. 将当前目录的子目录和子文件分开，
        #   将目录储存于dir_list，
        #   将文件储存于file_list
        # 1. Split sub-files and sub-folders into two lists,
        #   sub-folders will store into dir_list,
        #   sub-files will store into file_list
        for file_dir in file_dir_list:
            file_dir_path = os.path.join(section_path, file_dir)
            if os.path.isdir(file_dir_path):
                dir_list.append(os.path.relpath(file_dir_path, notebook_root))
            elif os.path.isfile(file_dir_path) and (
                    Path(file_dir_path).suffix.lower() in NotebookProcessor.PROCESS_FILE_TYPE_LIST):
                file_list.append(os.path.relpath(file_dir_path, notebook_root))
        # 2. 处理section基本信息，有：
        # 目录相对路径
        # 目录section名称
        # 目录创建时间
        # 目录最后更新时间
        # 2. Deal with section's basic info，includes:
        # current rel path
        # current section info
        # current section creation time
        # current section modification time
        section_dict = copy.deepcopy(NotebookProcessor.SECTION_DICT)
        section_dict[NotebookProcessor.SECTION_DICT_REL_PATH] = os.path.relpath(section_path, notebook_root)
        section_dict[NotebookProcessor.SECTION_DICT_SECTION_NAME] = os.path.basename(section_path)
        section_dict[NotebookProcessor.SECTION_DICT_SECTION_CREATION_TIME] = \
            time.ctime(os.path.getctime(section_path))
        section_dict[NotebookProcessor.SECTION_DICT_SECTION_UPDATE_TIME] = [
            time.ctime(os.path.getmtime(section_path))]
        # 3. 处理子目录相关信息，有：
        #   子目录与笔记本根目录对应的相对路径
        # 3. Deal with sub-notes related info, includes：
        #   sub-folders vs notebook's root rel path
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
        # 4. deal with sub-notes info, includes：
        # sub-file vs notebook's root rel path
        # sub-file file type
        # sub-file name (include file extension)
        # sub-file creation time
        # sub-file final modification time
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
        # 5. write section info
        section_json_file = open(os.path.join(section_path, NotebookProcessor.PATH_REL_SECTION_JSON), "w+")
        section_json_file.write(json.dumps(section_dict))
        section_json_file.close()
        return section_dict

    # 📕 核心功能
    # 更新指定的的笔记本section和笔记的信息
    # ⬇️ 参数
    # ori_section_dict: 原section的信息字典
    # section_path_full: 系统中section的绝对路径
    # notebook_root: 笔记本的根目录（即笔记本的源仓库所在位置）
    # ⬆️ 返回值
    # section_dict: 当前section的信息字典
    # 🎯️ 应用
    # NotebookProcessor.check_section_json()
    # ------------------------------------------------------------------------------------------------------------------
    # 📕 Core function
    # Update the specific notebook's section and note info
    # ⬇️ Parameter:
    # ori_section_dict: Original section info dict
    # section_path_full: Section full path in system
    # notebook_root: Notebook's root location (resource repository location)
    # ⬆️ Return
    # section_dict: current section's info dict
    # 🎯Usage:
    # NotebookProcessor.check_section_json()
    @staticmethod
    def __update_section_json(ori_section_dict, section_path_full, notebook_root):
        dirs_dict = ori_section_dict[NotebookProcessor.SECTION_DICT_SUB_SECTION_REL_PATH_DICT]
        files_dict = ori_section_dict[NotebookProcessor.SECTION_DICT_NOTES_DICT]

        new_dir_file_list = NotebookProcessor.__get_dir_file_list(section_path_full, notebook_root)

        modified_flag = False
        # 1. 检查section基本信息
        # 1. check section basic info
        ori_section_dict[NotebookProcessor.SECTION_DICT_SECTION_UPDATE_TIME].append(time.ctime(time.time()))
        ori_path = ori_section_dict[NotebookProcessor.SECTION_DICT_REL_PATH]
        cur_path = os.path.relpath(section_path_full, notebook_root)
        if ori_path != cur_path:
            modified_flag = True
            ori_section_dict[NotebookProcessor.SECTION_DICT_REL_PATH] = cur_path
        # 2. 检查sub-section的增减
        # 2. Check sub-sections if have sub-sections added or removed
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
                        new_key = "0"
                    else:
                        new_key = "%s" % (int(keys_list[len(keys_list) - 1]) + 1)
                    dirs_dict[new_key] = add_folder
                    print("%s folder added." % str(os.path.join(section_path_full, add_folder)))
        # 3. 检查sub-notes的增减
        # 3. Check sub-notes if sub-notes added or removed
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
            # 3.1 笔记删除
            # 3.1 Notes removed
            if len(del_notes_list) > 0:
                for del_note_path in del_notes_list:
                    note_index = ori_notes_dict[del_note_path]
                    del_file = files_dict[note_index][NotebookProcessor.NOTE_DICT_NOTE_FILE_PATH_REL]
                    files_dict.pop(note_index)
                    print("%s note removed." % str(os.path.join(section_path_full, del_file)))
            # 3.2 笔记增加
            # 3.2 Notes added
            if len(add_notes_list) > 0:
                for note_file_name in add_notes_list:
                    note_file_name = os.path.join(notebook_root, note_file_name)
                    note_file_path_full = note_file_name
                    note_file_path_rel = os.path.relpath(note_file_path_full, notebook_root)
                    note_suffix = Path(note_file_name).suffix.lower()
                    note_name = str(os.path.basename(note_file_name).split(".")[0])
                    note_ctime = time.ctime(os.path.getctime(note_file_name))
                    note_mtime = time.ctime(os.path.getmtime(note_file_name))
                    if len(files_dict) == 0:
                        new_key = 0
                    else:
                        last_key = int(list(files_dict.keys())[-1]) + 1
                        new_key = last_key
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
        # 4. 检查sub-notes的更新
        # 4. check if sub-notes have update
        for note_key, note_dict in files_dict.items():
            old_path = os.path.join(notebook_root, note_dict[NotebookProcessor.NOTE_DICT_NOTE_FILE_PATH_REL])
            new_path = os.path.join(notebook_root, files_dict[note_key][NotebookProcessor.NOTE_DICT_NOTE_FILE_PATH_REL])
            rel_path = os.path.relpath(new_path, notebook_root)
            if old_path != new_path:
                modified_flag = True
                files_dict[note_key][NotebookProcessor.NOTE_DICT_NOTE_FILE_PATH_REL] = rel_path

            new_mtime = time.ctime(os.path.getctime(old_path))
            ori_mtime = note_dict[NotebookProcessor.NOTE_DICT_MODIFICATION_TIME]

            if new_mtime not in ori_mtime:
                modified_flag = True
                files_dict[note_key][NotebookProcessor.NOTE_DICT_MODIFICATION_TIME].append(new_mtime)
        # 5. 如果当前section有状态更新，那么重新写入
        # 5. If current section has info update，rewrite .section.json
        if modified_flag:
            section_json_path_full = os.path.join(section_path_full, NotebookProcessor.PATH_REL_SECTION_JSON)
            section_json_file = open(section_json_path_full, "w+")
            section_json_file.write(json.dumps(ori_section_dict))
            section_json_file.close()
        return ori_section_dict

    # 📕 核心功能
    # 获取当前文件夹的子文件夹及其子文件
    # ⬇️ 参数
    # section_path_full: 系统中section的绝对路径
    # notebook_root: 笔记本的根目录（即笔记本的源仓库所在位置）
    # ⬆️ 返回值
    # 作为元组返回
    # dir_list: 在 tuple[0], 储存子文件夹的名字
    # file_list: 在 tuple[0], 储存子文件的名字
    # 🎯️ 应用
    # NotebookProcessor.__update_section_json()
    # ------------------------------------------------------------------------------------------------------------------
    # 📕 Core function
    # Get current directory's sub-directories and sub-notes
    # ⬇️ Parameter:
    # section_path: Section full path in system
    # notebook_root: Notebook's root location (resource repository location)
    # ⬆️ Return
    # return as a tuple
    # dir_list: at tuple[0], stores all sub-dirs' name
    # file_list: at tuple[0], stores all sub-files' name
    # 🎯Usage:
    # NotebookProcessor.__update_section_json()
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
