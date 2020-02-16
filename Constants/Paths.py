import os
from pathlib import Path


class Paths:
    # ------------------------------------------------------------------------------------------------------------------
    PATH_FULL_SYS_LOCATION = Path(Path(os.path.dirname(__file__)).parent)
    # ------------------------------------------------------------------------------------------------------------------
    # 系统配置目标地
    PATH_RELA_NOTEBOOKS_RES_LOCATION_JSON = "configs/note_books_resource.json"
    PATH_FULL_NOTEBOOKS_RES_LOCATION_JSON = os.path.join(PATH_FULL_SYS_LOCATION, PATH_RELA_NOTEBOOKS_RES_LOCATION_JSON)

    PATH_RELA_NOTEBOOKS_DEST_LOCATION_JSON = "configs/note_books_destination.json"
    PATH_FULL_NOTEBOOKS_DEST_LOCATION_JSON = os.path.join(PATH_FULL_SYS_LOCATION,
                                                          PATH_RELA_NOTEBOOKS_DEST_LOCATION_JSON)

    PATH_RELA_NOTEBOOKS_THEME_JSON = "configs/note_books_themes.json"
    PATH_FULL_NOTEBOOKS_THEME_JSON = os.path.join(PATH_FULL_SYS_LOCATION, PATH_RELA_NOTEBOOKS_THEME_JSON)
    # ------------------------------------------------------------------------------------------------------------------
    # 笔记本输出目标地
    PATH_FULL_NOTEBOOK_DEST = ""

    PATH_RELA_NOTEBOOK_SCRIPTS_DEST = "source"
    PATH_FULL_NOTEBOOK_SCRIPTS_DEST = ""

    PATH_FULL_NOTEBOOK_INFO_JS_DEST = ""
    PATH_RELA_NOTEBOOK_INFO_JS_DEST = ""

    PATH_FULL_NOTEBOOK_REPOSITORY = ""

    # 📕 核心功能
    # 设置单笔记本的相关目标文件夹
    # ⬇️ 输入参数
    # notebook_root: 笔记本的根目录（即笔记本的源仓库所在位置）
    # notebook_dest: 笔记本目标跟目录 （即笔记最后储存未知）
    # ------------------------------------------------------------------------------------------------------------------
    # 📕 Core function
    # Setup a notebook's related destination folder
    # ⬇️ Input argument
    # notebook_root: Notebook's root location (resource repository location)
    # notebook_dest: Notebook's destination location (destination repository location)
    @staticmethod
    def set_dest_path(notebook_dest, notebook_root):
        Paths.PATH_FULL_NOTEBOOK_DEST = notebook_dest
        Paths.PATH_FULL_NOTEBOOK_SCRIPTS_DEST = os.path.join(notebook_dest, Paths.PATH_RELA_NOTEBOOK_SCRIPTS_DEST)
        Paths.PATH_FULL_NOTEBOOK_INFO_JS_DEST = "%s/js/note_info.js" % Paths.PATH_FULL_NOTEBOOK_SCRIPTS_DEST
        Paths.PATH_RELA_NOTEBOOK_INFO_JS_DEST = "%s/js/note_info.js" % Paths.PATH_RELA_NOTEBOOK_SCRIPTS_DEST
        Paths.PATH_FULL_NOTEBOOK_REPOSITORY = notebook_root
    # ------------------------------------------------------------------------------------------------------------------
    # 笔记本脚本配置
    scripts_files_dict = {
        ""
    }
