import json
import logging
import os
import sys

from Processor.Constants.Paths import Paths
from Processor.DestinationProcessor import DestinationProcessor
from Processor.ResourceProcessor import ResourceProcessor
from Processor.Exception.Exceptions import WrongNoteBookPathError


class SysProcessor:
    check_configs = {
        Paths.PATH_FULL_NOTEBOOKS_RES_LOCATION_JSON: {},
        Paths.PATH_FULL_NOTEBOOKS_THEME_JSON: {"current": "default", "default": "default"}
    }

    # Check system config, if not exit or invalid config will write default config
    # 将笔记本系统添加进系统设置, 如果不存在或者非法将写入默认的配置
    # @Return:
    # No return
    @staticmethod
    def configs_check():
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
            DestinationProcessor.initial_notebooks_repository()
        else:
            try:
                with open(Paths.PATH_FULL_NOTEBOOKS_DEST_LOCATION_JSON, "r") as config_file:
                    json.loads(config_file.read())
            except json.decoder.JSONDecodeError:
                DestinationProcessor.initial_notebooks_repository()

    # Get the processing notebook(s) names
    # It has two mode:
    #   1. Enter a a specific notebook repository to process
    #   2. Choose notebook repository(ies) stored in system config
    # 获取即将处理的笔记本的名称
    #   1. 输入一个指定即将要处理的笔记仓库的名字
    #   2. 选择存储在系统配置中的笔记本（们）
    # @Return:
    # processing_list: List of checked notebook repositories going to be processed
    # processing_list: 即将处理的笔记仓库list
    @staticmethod
    def get_processing_notebooks_list():
        processing_notebooks_list = []
        note_book_root = ""
        # 1. Get processing notebook(s)'s name
        try:
            note_book_loc_index = sys.argv.index("-g") + 1
            rel_path = sys.argv[note_book_loc_index]
            # Is a directory
            if os.path.isdir(note_book_root):
                note_book_root = os.path.abspath(rel_path)
                # A directory without write permission
                if not os.access(note_book_root, os.W_OK):
                    raise PermissionError
                # A directory with write permission
                else:
                    processing_notebooks_list.append(note_book_root)
            # Is not A notebook mode
            # OR
            # Is not a directory
            else:
                if rel_path[0] is "-":
                    raise IndexError
                else:
                    raise WrongNoteBookPathError
        except IndexError:
            processing_notebooks_list = SysProcessor.__get_user_target_notebooks()
        except PermissionError:
            logging.error("Notebook folder \"%s\" permission error!" % note_book_root)
            logging.critical("Do you want to process the other notebooks stored in system?")
            if input().lower() in ["y", "yes"]:
                processing_notebooks_list = SysProcessor.__get_user_target_notebooks()
            else:
                return processing_notebooks_list
        except WrongNoteBookPathError:
            logging.error("Notebook folder \"%s\" path error!" % note_book_root)
            logging.critical("Do you want to process the others notebooks stored in system?")
            if input().lower() in ["y", "yes"]:
                processing_notebooks_list = SysProcessor.__get_user_target_notebooks()
            else:
                return processing_notebooks_list
        # 2. If a new repository add to system config
        if len(processing_notebooks_list) == 1:
            new_note_book_path = processing_notebooks_list[0]
            SysProcessor.add_new_repository(new_note_book_path)
        return processing_notebooks_list

    # Choose processing notebook(s) from notebook repository(ies) stored in system
    # 从系统储存的笔记本中选择要处理的笔记本
    # @Return:
    # result: List of checked notebook repositories going to be processed
    # result: 即将处理的笔记仓库list
    # @For:
    # SysProcessor.get_processing_notebooks_list()
    @staticmethod
    def __get_user_target_notebooks():
        all_notebooks = ResourceProcessor.get_resource_notebooks_paths()
        if len(all_notebooks) == 0:
            return all_notebooks
        while True:
            result = []
            notice = "Enter notebooks' number. (Multiple notebooks split them by \",\")"
            print(notice)

            temp_list = SysProcessor.__print_list(all_notebooks)
            input_list = input().split(",")
            choices = [i for i in input_list if i in temp_list]
            if len(choices) > 0:
                for num in temp_list:
                    result.append(all_notebooks[int(num) - 1])
                print("Following repository will be processed. Do you confirm?")
                SysProcessor.__print_list(result)
                confirm = input().lower()
                if confirm in ["y", "yes"]:
                    return result
                else:
                    logging.critical("Re-choose notebook repositories!")
            else:
                logging.critical("Wrong input choices! Please enter correct one.")

    # Print system stored notebook repository(ies)
    # 打印系统储存的笔记本仓库
    # @Input:
    # in_list: List need to print
    # @Return:
    # temp_list:
    # temp_list:
    # @For:
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

    # Add notebook repository to system config
    # 将笔记本系统添加进系统设置
    # @Input:
    # new_notebook_path: a new notebook path will add to system config
    # new_notebook_path: 一个将加入到系统中的新的笔记本仓库路径
    @staticmethod
    def add_new_repository(new_notebook_path):
        if new_notebook_path not in ResourceProcessor.get_resource_notebooks_info():
            new_note_book_info_dict = ResourceProcessor.get_new_notebook_info(new_notebook_path)
            ResourceProcessor.add_resource_notebook(new_notebook_path, new_note_book_info_dict)

    # Delete notebook repository from system config
    # 从一个笔记本系统中将移除的旧的笔记本仓库移除
    # @Input:
    # old_notebook_path: a old notebook path will add remove from system config
    # old_notebook_path: 一个将从笔记本系统中移除的旧的笔记本仓库路径
    @staticmethod
    def del_old_repository(old_notebook_path):
        raise NotImplementedError
