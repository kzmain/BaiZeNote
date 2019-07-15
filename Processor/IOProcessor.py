import json
import os
import shutil
from datetime import datetime

from Processor.Constants.Paths import Paths


class IOProcessor:
    # 📕 核心功能：
    # 将新的笔记本及相关信息的字典写入到系统配置
    # ⬇️ 参数：
    # note_book_path: 新笔记本路径
    # note_book_info_dict: 新笔记本信息的字典
    # ⬆️ 返回值：
    # None
    # ------------------------------------------------------------------------------------------------------------------
    # 📕 Core function:
    # Write dictionary to system configuration for NEW notebook and related information
    # ⬇️ Parameter:
    # note_book_path: New notebook full path
    # note_book_info_dict: New notebook info dictionary
    # ⬆️ Return:
    # None
    @staticmethod
    def add_new_notebook_info(note_book_path, note_book_info_dict):
        all_note_books_dict = IOProcessor.get_sys_notebooks_info()
        if note_book_path not in all_note_books_dict:
            all_note_books_dict[note_book_path] = note_book_info_dict
            IOProcessor.write_notebooks_info(all_note_books_dict)

    # 📕 核心功能：
    # 写入所有笔记本及相关信息的字典到系统配置
    # ⬇️ 参数：
    # all_note_books_dict: 所有笔记本储存位置及相关信息的字典
    # ⬆️ 返回值：
    # None
    # ------------------------------------------------------------------------------------------------------------------
    # 📕 Core function:
    # Write dictionary to system configuration for ALL notebooks and related information
    # ⬇️ Parameter:
    # all_note_books_dict: dictionary of stored notebooks and related info
    # ⬆️ Return:
    # None
    @staticmethod
    def write_notebooks_info(all_note_books_dict):
        if os.path.exists(Paths.PATH_FULL_NOTEBOOKS_RES_LOCATION_JSON):
            old_file_name = Paths.PATH_FULL_NOTEBOOKS_RES_LOCATION_JSON
            new_file_name = "%s%s%s" % (Paths.PATH_FULL_NOTEBOOKS_RES_LOCATION_JSON, str(datetime.today()), ".backup")
            shutil.copy(old_file_name, new_file_name)
        all_note_books_json_file = open(Paths.PATH_FULL_NOTEBOOKS_RES_LOCATION_JSON, "w+")
        all_note_books_json_file.write(json.dumps(all_note_books_dict))
        all_note_books_json_file.close()

    # 📕 核心功能：
    # 从系统配置中提取储存的笔记本及相关信息的字典
    # ⬆️ 返回值：
    # result_dict: 配置中提取储存的笔记本储存位置及相关信息的字典
    # ------------------------------------------------------------------------------------------------------------------
    # 📕 Core function:
    # Get the dictionary of stored notebooks and related info from the system configuration
    # ⬆️ Return:
    # result_dict: dictionary of stored notebooks and related info from the system configuration
    @staticmethod
    def get_sys_notebooks_info():
        result_json_file = open(Paths.PATH_FULL_NOTEBOOKS_RES_LOCATION_JSON, "r+")
        result_dict = json.loads(result_json_file.read())
        result_json_file.close()
        return result_dict

    # 📕 核心功能
    # 从系统配置中提取储存的笔记本列表
    # ⬆️ 返回值
    # result: 系统储存的笔记本列表
    # ------------------------------------------------------------------------------------------------------------------
    # 📕 Core function
    # Get the list of stored notebooks from the system configuration
    # ⬆️ Return
    # result: System stored notebook list
    @staticmethod
    def get_sys_notebooks_paths():
        result = list(IOProcessor.get_sys_notebooks_info())
        return result
