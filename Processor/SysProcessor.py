import json
import logging
import os
import sys
import time

from Constants import SysArgument
from Constants.Paths import Paths
from Processor.Exception.Exceptions import WrongNoteBookPathError
from Processor.IOProcessor import IOProcessor


class SysProcessor:
    check_configs = {
        Paths.PATH_FULL_NOTEBOOKS_RES_LOCATION_JSON: {},
        Paths.PATH_FULL_NOTEBOOKS_THEME_JSON: {"current": "default", "default": "default"}
    }

    # 📕 核心功能
    # 将笔记本系统添加进系统设置, 如果不存在或者非法将写入默认的配置
    # ⬆️ 返回值
    # None
    # ------------------------------------------------------------------------------------------------------------------
    # 📕 Core function
    # Check system configs, if not exist, create them with default value
    # ⬆️ Return
    # None
    @staticmethod
    def sys_configs_check():
        for path, default_value in SysProcessor.check_configs.items():
            if not os.path.exists(path):
                with open(path, "w+") as config_file:
                    config_file.write(json.dumps(default_value))
            else:
                with open(path, "r") as config_file:
                    try:
                        json.loads(config_file.read())
                    except json.decoder.JSONDecodeError:
                        with open(path, "w+") as con_file:
                            con_file.write(json.dumps(default_value))
        if not os.path.exists(Paths.PATH_FULL_NOTEBOOKS_DEST_LOCATION_JSON):
            return "notebooks_repository"
        else:
            try:
                with open(Paths.PATH_FULL_NOTEBOOKS_DEST_LOCATION_JSON, "r") as config_file:
                    json.loads(config_file.read())
            except json.decoder.JSONDecodeError:
                return "notebooks_repository"

    # 📕 核心功能
    # 获取用户需要处理的笔记本源文件列表
    # 他有两个模式：
    #   1. 输入一个指定即将要处理的笔记仓库的名字
    #   2. 选择存储在系统配置中的笔记本（们）
    # ⬆️ 返回值
    # notebook_list: 用户需要处理的笔记本源文件列表
    # ------------------------------------------------------------------------------------------------------------------
    # 📕 Core function
    # Get a list of notebook source files that users need to process
    # It has two mode:
    #   1. Enter a a specific notebook repository to process
    #   2. Choose notebook repository(ies) stored in system config
    # ⬆️ Return
    # notebook_list: notebook source files that users need to process
    @staticmethod
    def get_processing_notebooks_list():
        notebook_list = []
        note_book_root = ""
        # 1. Get processing notebook(s)'s name
        # 1. 获取需要处理的笔记本名称
        try:
            note_book_loc_index = sys.argv.index(SysArgument.NOTEBOOKS_GENERATE_FLAG) + 1
            note_book_root = sys.argv[note_book_loc_index]
            # 1.1.1 指定文件夹模式
            # 1.1.1 Specific repository mode
            if os.path.isdir(note_book_root):
                note_book_root = os.path.abspath(note_book_root)
                # A directory without write permission
                if not os.access(note_book_root, os.W_OK):
                    raise PermissionError
                # A directory with write permission
                else:
                    notebook_list.append(note_book_root)
            # 1.1.2
            # 不需要处理特殊笔记本
            # 或者
            # 输入的不是repository
            # 1.1.2
            # NOT Specific repository mode
            # OR
            # After "-g" is not a repository
            else:
                if note_book_root[0] is "-":
                    raise IndexError
                else:
                    raise WrongNoteBookPathError
        # 1.1.3 不管之前是什么exception，都询问用户是否进入系统配置选择已有的仓库
        # 1.1.3  Regardless of the previous exception,
        # ask if user want to enter the system configuration to select an existing warehouse.
        except IndexError:
            notebook_list = SysProcessor.__get_in_sys_notebooks()
        except PermissionError:
            logging.error("Notebook folder \"%s\" permission error!" % note_book_root)
            logging.critical("Do you want to process the other notebooks stored in system?")
            if input().lower() in ["y", "yes"]:
                notebook_list = SysProcessor.__get_in_sys_notebooks()
            else:
                return notebook_list
        except WrongNoteBookPathError:
            logging.error("Notebook folder \"%s\" path error!" % note_book_root)
            logging.critical("Do you want to process the others notebooks stored in system?")
            if input().lower() in ["y", "yes"]:
                notebook_list = SysProcessor.__get_in_sys_notebooks()
            else:
                return notebook_list
        # 2. 如果是一个新的笔记本将其加入到系统
        # 2. If a new notebook repository add to system config
        if len(notebook_list) == 1:
            new_note_book_path = notebook_list[0]
            SysProcessor.__add_new_repository(new_note_book_path)
        return notebook_list

    # 📕 核心功能
    # 从系统储存的笔记本中选择要处理的笔记本
    # ⬆️ 返回值
    # result: 用户选择的需要处理的笔记本源文件列表
    # 🎯️ 应用
    # SysProcessor.get_processing_notebooks_list()
    # ------------------------------------------------------------------------------------------------------------------
    # 📕 Core function
    # Choose processing notebook(s) from notebook repository(ies) stored in system
    # ⬆️ Return
    # result: List of notebook source files selected by the user to be processed
    # 🎯Usage:
    # SysProcessor.get_processing_notebooks_list()
    @staticmethod
    def __get_in_sys_notebooks():
        all_notebooks = IOProcessor.get_sys_notebooks_paths()
        # 1. 系统中没有文件 退出
        if len(all_notebooks) == 0:
            logging.critical("No note book in system, Exit!")
            sys.exit(1)
        # 2. 返回用户选择的list
        while True:
            result = []
            notice = "Enter notebooks' number. (Multiple notebooks split them by \",\"). Or \"all\" for all notebooks"
            print(notice)
            temp_list = SysProcessor.__print_list(all_notebooks)
            input_list = input().split(",")
            if "all" in input_list or "All" in input_list:
                input_list = temp_list
            choices = [i for i in input_list if i in temp_list]
            if len(choices) > 0:
                for num in choices:
                    result.append(all_notebooks[int(num) - 1])
                print("Following repository will be processed. Do you confirm?(y/n)")
                SysProcessor.__print_list(result)
                confirm = input().lower()
                if confirm in ["y", "yes"]:
                    return result
                elif confirm in ["n", "no"]:
                    pass
                else:
                    logging.critical("Re-choose notebook repositories!")
            else:
                logging.critical("Wrong input choices! Please enter correct one.")

    # 📕 核心功能
    # 从系统储存的笔记本中选择要处理的笔记本
    # ⬇️ 参数
    # in_list: 需要打印的元素list
    # ⬆️ 返回值
    # temp_list: 一列数字
    # 🎯️ 应用
    # SysProcessor.get_processing_notebooks_list()
    # ------------------------------------------------------------------------------------------------------------------
    # 📕 Core function
    # Choose processing notebook(s) from notebook repository(ies) stored in system
    # ⬇️ Parameter:
    # List of elements to be printed
    # ⬆️ Return
    # temp_list: List of number
    # 🎯Usage:
    # SysProcessor.get_processing_notebooks_list()
    @staticmethod
    def __print_list(in_list):
        table_line = "=========================================================================="
        table_outline = "--------------------------------------------------------------------------"
        count = 1
        temp_list = []
        print(table_line)
        for notebook in in_list:
            print(str(count) + "\t" + notebook)
            if not count == len(in_list):
                print(table_outline)
            temp_list.append(str(count))
            count += 1
        print(table_line)
        return temp_list

    # 📕 核心功能
    # 将笔记本系统添加进系统设置
    # ⬇️ 参数
    # new_notebook_path: 一个将加入到系统中的新的笔记本仓库路径
    # ⬆️ 返回值
    # None
    # 🎯️ 应用
    # SysProcessor.get_processing_notebooks_list()
    # ------------------------------------------------------------------------------------------------------------------
    # 📕 Core function
    # Add notebook repository to system config
    # ⬇️ Parameter:
    # new_notebook_path: a new notebook path will add to system config
    # ⬆️ Return
    # None
    # 🎯Usage:
    # SysProcessor.get_processing_notebooks_list()
    @staticmethod
    def __add_new_repository(new_notebook_path):
        if new_notebook_path not in IOProcessor.get_sys_notebooks_info():
            new_note_book_info_dict = SysProcessor.__get_new_notebook_info(new_notebook_path)
            IOProcessor.add_new_notebook_info(new_notebook_path, new_note_book_info_dict)

    # 📕 核心功能
    # 获取新笔记的相关信息
    # ⬇️ 参数
    # note_book_path_full: 新笔记本仓库路径
    # ⬆️ 返回值
    # note_book_dict: 新笔记相关信息
    # 🎯️ 应用
    # SysProcessor.get_processing_notebooks_list()
    # ------------------------------------------------------------------------------------------------------------------
    # 📕 Core function
    # Get new notebook related info
    # ⬇️ Parameter:
    # note_book_path_full: New notebook folder path
    # ⬆️ Return
    # note_book_dict: New notebook related info
    # 🎯Usage:
    # SysProcessor.get_processing_notebooks_list()
    @staticmethod
    def __get_new_notebook_info(note_book_path_full):
        while True:
            enter_author_string = "Please input notebook's author(s)'s name, " \
                                  "if multiple author please separate by comma \",\" : \n"
            confirm_author_string = "Is(Are) following your notebook's author(s) name(s)?(y/n)\n%s\n"
            author_raw = input(enter_author_string)
            author_list = author_raw.split(",")
            author_list = [x for x in author_list if x.strip()]
            if input(confirm_author_string % str(author_list)).lower() in ["yes", "y"]:
                break
        while True:
            enter_notebook_name = "Please enter a notebook name. If you want default name, press \"Enter\" directly"
            confirm_notebook_string = "Is following your notebook's name?(y/n)\n%s\n"
            notebook_name = input(enter_notebook_name)
            if notebook_name == "":
                notebook_name = os.path.basename(note_book_path_full)
            if input(confirm_notebook_string % notebook_name).lower() in ["yes", "y"]:
                break
        creation_time = time.ctime(os.path.getctime(note_book_path_full))
        note_book_dict = {"AUTHORS": author_list, "NOTEBOOK_NAME": notebook_name,
                          "CTIME": creation_time, "TAG": [], }
        return note_book_dict
