from Processor.HTMLProcessor import HTMLProcessor
from Processor.IOProcessor import IOProcessor
from Processor.NotebookProcessor import NotebookProcessor
from Processor.ResourceProcessor import ResourceProcessor
from Processor.SysProcessor import SysProcessor
from Processor.DestinationProcessor import DestinationProcessor


class CoreProcessor:
    # SysProcessor -----------------------------------------------------------------------------------------------------

    # # Delete notebook repository from system config
    # # 从一个笔记本系统中将移除的旧的笔记本仓库移除
    # # @Input:
    # # old_notebook_path: a old notebook path will add remove from system config
    # # old_notebook_path: 一个将从笔记本系统中移除的旧的笔记本仓库路径
    # @staticmethod
    # def del_old_repository(old_notebook_path):
    #     raise NotImplementedError

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
        if SysProcessor.sys_configs_check() == "notebooks_repository":
            CoreProcessor.initial_notebooks_repository()

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
    def sys_get_processing_notebooks_list():
        notebook_list = SysProcessor.get_processing_notebooks_list()
        return notebook_list

    # ResourceProcessor ------------------------------------------------------------------------------------------------

    # 📕 核心功能
    # 获取所有储存在系统中的笔记本源文件路径及笔记本信息{路径：信息}
    # ⬆️ 返回值
    # repo_dict: 系统中的笔记本源文件路径及其对应信息
    # ------------------------------------------------------------------------------------------------------------------
    # 📕 Core function
    # Get all notebook paths and notebook info stored in system {paths: notebook_info}
    # ⬆️ Return
    # repo_dict: all notebook paths and related notebook info stored in system
    @staticmethod
    def res_get_notebooks_info():
        repo_dict = IOProcessor.get_sys_notebooks_info()
        return repo_dict

    # 📕 核心功能
    # 检查所有笔记本源文件是否可用
    # ⬇️ 输入参数
    # notebooks_path_list: 要处理的笔记本源文件位置list
    # ⬆️ 返回值
    # valid_list: 合规的笔记本源文件位置list
    # ------------------------------------------------------------------------------------------------------------------
    # 📕 Core function
    # Check if all input notebook resource paths are valid
    # ⬇️ Input Arguments
    # notebooks_path_list: the new notebooks resource full paths that need to check validation
    # ⬆️ Return
    # valid_list: valid notebook resource paths' list
    @staticmethod
    def res_check_notebooks_validation(notebooks_path_list):
        valid_list = ResourceProcessor.check_resource_notebooks_validation(notebooks_path_list)
        return valid_list

    # DestinationProcessor ---------------------------------------------------------------------------------------------

    # 📕 核心功能
    # 获取所有笔记本输出储存位置
    # ⬆️ 返回值
    # repo_dest: 所有笔记本输出储存位置
    # ------------------------------------------------------------------------------------------------------------------
    # 📕 Core function
    # Get all notebook destination full path
    # ⬆️ Return
    # repo_dest: all notebook destination full path
    @staticmethod
    def get_notebooks_destination():
        return DestinationProcessor.get_notebooks_destination()

    # 📕 核心功能
    # 获取当前笔记本输出储存位置
    # ⬇️ 输入参数
    # note_books_dest: 所有笔记本储存位置
    # notebook_name: 当前笔记本名字
    # ⬆️ 返回值
    # repo_dest: 当前笔记本输出储存位置
    # ------------------------------------------------------------------------------------------------------------------
    # 📕 Core function
    # Get current notebook destination full path
    # ⬇️ Input Arguments
    # note_books_dest: All notebooks destination
    # notebook_name: Current notebook name
    # ⬆️ Return
    # repo_dest: destination full path
    @staticmethod
    def get_notebook_destination(note_books_dest, notebook_name):
        repo_dest = DestinationProcessor.get_notebook_destination(note_books_dest, notebook_name)
        return repo_dest

    # 📕 核心功能
    # 初始化所有笔记本默认储存位置
    # ⬆️ 返回值
    # default_dest: 笔记本默认储存位置
    # ------------------------------------------------------------------------------------------------------------------
    # 📕 Core function
    # Initial all notebook default destination repository
    # ⬆️ Return
    # default_dest: default destination repository
    @staticmethod
    def initial_notebooks_repository():
        default_dest = DestinationProcessor.initial_notebooks_repository()
        return default_dest

    # 📕 核心功能
    # 删除目标文件夹旧的文件，建立新的笔记结构
    # ⬆️ 返回值
    # None
    # ------------------------------------------------------------------------------------------------------------------
    # 📕 Core function
    # Delete the corresponding old notebook in destination folder, set up new notebook structure
    # ⬆️ Return
    # None
    @staticmethod
    def prepare_file_writing():
        return DestinationProcessor.prepare_file_writing()

    # 📕 核心功能
    # 将原本笔记转化为html版本
    # ⬇️ 输入参数
    # notebook: 内存中的Notebook
    # nodes_dict: 每个section信息（简化版本）
    # ⬆️ 返回值
    # nodes_dict: 每个section信息（增加了HTML以及HTML_PATH_REL的信息）
    # ------------------------------------------------------------------------------------------------------------------
    # 📕 Core function
    # Convert original notes to html version
    # ⬇️ Input argument
    # notebook: Notebook in memory
    # nodes_dict: Include every section's info (Simplify version)
    # ⬆️ Return
    # nodes_dict: Include every section's info（Added HTML and HTML_PATH_REL的 info）
    @staticmethod
    def write_converted_htmls(notebook, nodes_dict):
        # TODO What to do when note status lock / hide tag/reference and so on
        nodes_dict = DestinationProcessor.write_converted_htmls(notebook, nodes_dict)
        return nodes_dict

    # 📕 核心功能
    # 在"-(r)server"模式下，为每个笔记生成静态页面
    # ⬇️ 输入参数
    # nodes_dict: 每个section信息（简化版本）
    # html_head: html 头文件
    # html_foot: html 尾文件
    # ⬆️ 返回值
    # None
    # ------------------------------------------------------------------------------------------------------------------
    # 📕 Core function
    # Under "-(r)server" mode, generate static pages for each note
    # ⬇️ Input argument
    # nodes_dict: Include every section's info (Simplify version)
    # html_head: html header
    # html_foot: html footer
    # ⬆️ Return
    # None
    @staticmethod
    def server_mode_write_page_html(html_path_rel, html_head, html_body):
        return DestinationProcessor.server_mode_write_page_html(html_path_rel, html_head, html_body)

    # 📕 核心功能
    # 为"-(r)local"模式写入index.html
    # ⬇️ 输入参数
    # html_head: html 头文件
    # html_body: html 中间部分
    # ⬆️ 返回值
    # None
    # ------------------------------------------------------------------------------------------------------------------
    # 📕 Core function
    # Write index.html for "(-r)local"
    # ⬇️ Input argument
    # html_head: html header
    # html_body: html body
    # ⬆️ Return
    # None
    @staticmethod
    def local_mode_write_index_html(html_head, html_body):
        return DestinationProcessor.local_mode_write_index_html(html_head, html_body)

    # 📕 核心功能
    # 写入静态文件到目标文件夹（主要包括：.js/.css/图片文件/影音文件/section-menu.blade.html）
    # ⬇️ 输入参数
    # files_dict: 静态文件字典（包含图片文件/影音文件）
    # ⬆️ 返回值
    # lib_dict: 库文件字典（包含.js/.css文件）
    # ------------------------------------------------------------------------------------------------------------------
    # 📕 Core function
    # Write static files to destination folder (Mainly include: .js/.css/image file/media file/section-menu.blade.html)
    # ⬇️ Input argument
    # files_dict: Static file dictionary (include info of image files and media files)
    # ⬆️ Return
    # lib_dict: Scripts static files dictionary (include .js/.css files)
    @staticmethod
    def write_static_resources(files_dict):
        lib_dict = DestinationProcessor.write_static_resources(files_dict)
        return lib_dict

    # NotebookProcessor ------------------------------------------------------------------------------------------------

    # 📕 核心功能
    # 检查每个section下的section.json，
    #   如果一个section没有section.json则初始化，
    #   如果一个section有section.json则检查，有必要的话则重新初始化或更新
    # ⬇️ 输入参数
    # notebook_root: 笔记的源目录
    # ⬆️ 返回值
    # section_dict: 包含所有section信息的字典（未精简版本）
    # ------------------------------------------------------------------------------------------------------------------
    # 📕 Core function
    # Check file section.json for each section (folder)
    #   If a section does not have section.json then initial it
    #   if a section has section.json then check it, if it is necessary this function will initial it or update it
    # ⬇️ Input argument
    # notebook_root: Notebook resource folder
    # ⬆️ Return
    # section_dict: A dictionary of all sections' info (not simplified version)
    @staticmethod
    def notebook_check_section_json(notebook_root):
        section_dict = NotebookProcessor.check_section_json(notebook_root)
        return section_dict

    # HTMLProcessor ----------------------------------------------------------------------------------------------------

    # 📕 核心功能
    # 生成头文件HTML
    # ⬇️ 输入参数
    # static_file_dict: 静态脚本文件字典
    # ⬆️ 返回值
    # html_header: 头文件
    # ------------------------------------------------------------------------------------------------------------------
    # 📕 Core function
    # Generate footer html
    # ⬇️ Input argument
    # static_file_dict: Static script files dict
    # ⬆️ Return
    # html_header: HTML header
    @staticmethod
    def generate_html_header(static_file_dict, sections_dict):
        html_header = HTMLProcessor.generate_html_header(static_file_dict, sections_dict)
        return html_header

    # 📕 核心功能
    # 生成尾文件HTML
    # ⬇️ 输入参数
    # static_file_dict: 静态脚本文件字典
    # ⬆️ 返回值
    # html_footer: 尾文件
    # ------------------------------------------------------------------------------------------------------------------
    # 📕 Core function
    # Generate footer html
    # ⬇️ Input argument
    # static_file_dict: Static script files dict
    # ⬆️ Return
    # html_footer: HTML footer
    @staticmethod
    def generate_html_footer(static_file_dict):
        html_footer = HTMLProcessor.generate_html_footer(static_file_dict)
        return html_footer

    # 📕 核心功能
    # 为 "-local"/"-rlocal" 生成 index.html 的body
    # 为 "-server"/"-rserver" 生成 对应每个页面的body
    # ⬇️ 输入参数
    # html_foot: 尾文件的HTML
    # old_node_dict: 原node_dict未更改
    # new_node_dict: node_dict已更改，为section版本简化版
    # ⬆️ 返回值
    # html_body: "(r)local" 或 for "(r)server" 模式的 html body部分
    # ------------------------------------------------------------------------------------------------------------------
    # 📕 Core function
    # Generate body html for "-local"/"-rlocal" mode's index.html
    # Generate body html for "-server"/"-rserver" mode's each note's body html
    # ⬇️ Input argument
    # html_foot: footer html
    # old_node_dict: Original node_dict, not modified
    # new_node_dict: Modified node_dict, is simplified by section
    # ⬆️ Return
    # html_body: The Body html for "(r)local" or for "(r)server" mode
    @staticmethod
    def generate_local_html_body(html_foot, node_dict, section_dict):
        html_body = HTMLProcessor.generate_local_html_body(html_foot, node_dict, section_dict)
        return html_body

    # 📕 核心功能
    # 为 "-server"/"-rserver" 生成 对应每个页面的body
    # ⬇️ 输入参数
    # html_foot: 尾文件的HTML
    # section_id: 要生成的note的section_id
    # note_id: 要生成的note的note_id
    # ⬆️ 返回值
    # html_body: "(r)server" 模式的 html body部分
    # ------------------------------------------------------------------------------------------------------------------
    # 📕 Core function
    # Generate body html for "-server"/"-rserver" mode's each note's body html
    # ⬇️ Input argument
    # notebook_root: footer html
    # section_id: Target note's section id
    # note_id: Target note's note id
    # ⬆️ Return
    # html_body: The Body html for "(r)local" or for "(r)server" mode
    @staticmethod
    def generate_server_html_body(html_foot, section_id, note_id):
        html_body = HTMLProcessor.generate_html_server_body(html_foot, section_id, note_id)
        return html_body
