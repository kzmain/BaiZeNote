import logging
import os

from Processor.IOProcessor import IOProcessor


class ResourceProcessor:
    # 📕 核心功能
    # 检查即将处理的笔记仓库的权限
    # 如果非法将其从处理列表与系统设置中移除
    # ⬇️ 参数
    # processing_list: 即将处理的笔记仓库list
    # ⬆️ 返回值
    # processing_list: 检查过后即将处理的笔记仓库list
    # ------------------------------------------------------------------------------------------------------------------
    # 📕 Core function
    # Check processing notebook repositories permission
    # If invalid remove it from processing list and system's config
    # ⬇️ Parameter:
    # processing_list: List of notebook repositories going to be processed
    # ⬆️ Return
    # processing_list: List of checked notebook repositories going to be processed
    @staticmethod
    def check_resource_notebooks_validation(processing_list):
        result_list = processing_list
        all_note_books_dict = IOProcessor.get_sys_notebooks_info()
        modified_flag = False
        # 1. 检查每个笔记本的相关信息
        # 1. Check each notebook's permission
        for path in processing_list:
            # Check a notebook repository's config

            if not os.path.isdir(path) or not os.access(path, os.W_OK):
                error_info = "\"%s\" no longer existed or have permission error, will remove from system" % path
                logging.critical(error_info)
                all_note_books_dict.pop(path, None)
                result_list.remove(path)
                modified_flag = True
        # 1. 当系统配置被更改，更新系统配置
        # 2. When system config modified, update system config
        if modified_flag:
            IOProcessor.write_notebooks_info(all_note_books_dict)
        return result_list
