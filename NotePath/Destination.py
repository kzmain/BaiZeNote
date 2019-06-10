import json
import logging
import os
import re
import shutil
import sys

from HTML.HTML import HTML
from NotePath.BaiZeSys import BaiZeSys
from NotePath.Source import Source
from Tools.File import File
import emarkdown.markdown as md


class Destination:
    BAIZE_REPO_NAME = "BaiZeNote"
    BAIZE_REPO_SUB_FOLDERS_LIST = ["server", "local", "server/sources", "local/sources"]

    PATH_RELA_NOTEBOOKS_REPO_LOCATION_JSON = BaiZeSys.PATH_RELA_NOTEBOOKS_REPO_LOCATION_JSON
    NOTEBOOKS_REPO_LOCATION_KEY = BaiZeSys.NOTEBOOKS_REPO_LOCATION_KEY
    PATH_FULL_SYS = BaiZeSys.PATH_FULL_SYS

    @staticmethod
    def get_notebooks_destination():
        note_book_dest = ""
        note_books_repository = Destination.get_notebooks_repository()
        if "-d" in sys.argv:
            try:
                note_book_dest_index = sys.argv.index("-d") + 1
                note_book_dest = sys.argv[note_book_dest_index]
                note_book_dest = os.path.abspath(note_book_dest)
                if not os.path.exists(note_book_dest):
                    os.mkdir(note_book_dest)
                    Destination.__check_notebooks_dest_sub_folders(note_book_dest)
                if not os.access(note_book_dest, os.W_OK):
                    raise PermissionError
            except IndexError:
                logging.error("Notebook destination folder did not input!")
                logging.warning("Will use system default destination folder \"%s\". Do you want continue?(y/n)"
                                % note_books_repository)
                if input().lower() not in ["yes", "y"]:
                    return
                else:
                    note_book_dest = note_books_repository
            except PermissionError:
                logging.error("Notebook destination folder \"%s\" permission error!" % note_book_dest)
                logging.warning("Will use system default destination folder \"%s\". Do you want continue?(y/n)"
                                % note_books_repository)
                if input().lower() not in ["yes", "y"]:
                    return
                else:
                    note_book_dest = note_books_repository
        else:
            note_book_dest = note_books_repository
        return note_book_dest

    @staticmethod
    def get_notebook_destination(note_books_dest, notebook_name):
        if "-local" in sys.argv:
            note_book_dest = os.path.join(note_books_dest, "local", notebook_name)
        elif "-server" in sys.argv:
            note_book_dest = os.path.join(note_books_dest, "server", notebook_name)
        else:
            raise Exception
        return note_book_dest

    @staticmethod
    def get_notebooks_repository():
        note_book_repo_json_path_full = os.path.join(Destination.PATH_FULL_SYS,
                                                     Destination.PATH_RELA_NOTEBOOKS_REPO_LOCATION_JSON)
        if not os.path.isfile(note_book_repo_json_path_full):
            note_books_repo_path_full = Destination.initial_notebooks_repository()
        else:
            try:
                note_books_repo_json_file = open(note_book_repo_json_path_full, "r")
                note_books_repo_dict = json.loads(note_books_repo_json_file.read())
                note_books_repo_path_full = note_books_repo_dict[Destination.NOTEBOOKS_REPO_LOCATION_KEY]
                if not os.path.exists(note_books_repo_path_full):
                    os.mkdir(note_books_repo_path_full)
                if not os.access(note_books_repo_path_full, os.W_OK):
                    raise PermissionError
                else:
                    Destination.__check_notebooks_dest_sub_folders(note_books_repo_path_full)
            except PermissionError:
                logging.error("Permission denied! Please set a new notebooks repository!")
                os.remove(os.path.join(Destination.PATH_FULL_SYS, Destination.PATH_RELA_NOTEBOOKS_REPO_LOCATION_JSON))
                note_books_repo_path_full = Destination.initial_notebooks_repository()
            except IndexError:
                logging.error("BaiZe notebooks' repository config damaged! Please set a new notebooks repository!")
                os.remove(os.path.join(Destination.PATH_FULL_SYS, Destination.PATH_RELA_NOTEBOOKS_REPO_LOCATION_JSON))
                note_books_repo_path_full = Destination.initial_notebooks_repository()
        return note_books_repo_path_full

    @staticmethod
    def initial_notebooks_repository():
        while True:
            try:
                note_books_repo_path_full_raw = input("Please input a all notebooks repository folder:\n")
                note_books_repo_path_full = os.path.join(note_books_repo_path_full_raw, Destination.BAIZE_REPO_NAME)
                if Destination.PATH_FULL_SYS == os.path.commonpath(
                        [note_books_repo_path_full, Destination.PATH_FULL_SYS]):
                    raise PermissionError

                if os.path.exists(note_books_repo_path_full):
                    logging.warning(
                        "\"%s\" exists, do you still want use this folder as all notebooks' repository? (y/n)"
                        % note_books_repo_path_full)
                    if input().lower() in ["y", "yes"]:
                        pass
                    else:
                        continue
                else:
                    os.mkdir(note_books_repo_path_full)

                if not os.access(note_books_repo_path_full, os.W_OK):
                    raise PermissionError

                all_note_books_dest_dict = {
                    Destination.NOTEBOOKS_REPO_LOCATION_KEY: note_books_repo_path_full}
                note_books_repo_json_file_path_full = \
                    os.path.join(Destination.PATH_FULL_SYS, Destination.PATH_RELA_NOTEBOOKS_REPO_LOCATION_JSON)
                note_books_repo_json_file = open(note_books_repo_json_file_path_full, "w+")
                note_books_repo_json_file.write(json.dumps(all_note_books_dest_dict))
                note_books_repo_json_file.close()
                break
            except PermissionError:
                logging.error("Permission denied! Please enter another notebooks repository destination")
            except FileNotFoundError:
                logging.error("Folder location denied! Please enter another notebooks repository destination")

        Destination.__check_notebooks_dest_sub_folders(note_books_repo_path_full)
        return note_books_repo_path_full

    @staticmethod
    def prepare_file_writing(notebook_resource, notebook_destination):
        if os.path.exists(notebook_destination):
            shutil.rmtree(notebook_destination)
        File.folder_tree_copy(notebook_resource, notebook_destination)
        return

    @staticmethod
    def server_mode_write_converted_htmls(notebook, nodes_dict):
        # TODO What to do when note status lock / hide tag/reference and so on
        # TODO 后面emarkdown改了以后，generate 和 写入要分开
        for section_id, section_dict in nodes_dict.items():
            note_rel_list = []
            for note_id, note_dict in section_dict.items():
                note_rel_raw = note_dict[Source.SOURCE_SUB_NOTE_DICT_NOTE_FILE_PATH_REL]
                note_file_type = note_dict[Source.SOURCE_SUB_NOTE_DICT_NOTE_FILE_TYPE]
                note_html_rel_raw = re.sub("%s" % note_file_type, "", note_rel_raw, 1)
                next_name_counter = 0
                while note_html_rel_raw in note_rel_list:
                    note_html_rel_raw += str(next_name_counter)
                note_html_path_rel = "%s%s" % (note_html_rel_raw, ".html")
                note_html_resource_path_full = os.path.join(notebook.notebook_root, note_rel_raw)

                note_html_destination_path_full = os.path.join(notebook.notebook_dest, note_html_path_rel)
                note_html_destination_path_full += ".blade.html"

                note_dict[Source.SOURCE_SUB_NOTE_DICT_HTML_FILE_REL] = note_html_path_rel

                if note_file_type == ".md":
                    md.process(["-f", note_html_resource_path_full, "-d", note_html_destination_path_full])
        return nodes_dict
        print()
        # print()
        #
        # # 处理 .md，生成对应 .html文件
        # # Process .md file, generate it corresponding .html file
        # md_file_path_full = os.path.abspath(os.path.join(note.note_root, file_relative_location))
        # md.process(["-f", md_file_path_full])
        # # 打开本地对应 HTML 文件，读取 HTML 文件对应 .md 文件
        # # Open local html files and read .md file's .html
        # html_path_relative = re.sub(r"\.md$", ".html", file_relative_location)
        # html_file_path_full = os.path.abspath(os.path.join(note.note_root, html_path_relative))
        # html_file = open(html_file_path_full, "r")
        # html_code = html_file.read()
        # html_file.close()
        # if "-local" in sys.argv:
        #     html_code = URIReplacement.replace_img_uri(html_code, folder_path_relative)
        #     os.remove(html_file_path_full)
        # if "-server" in sys.argv:
        #     os.rename(html_file_path_full, html_file_path_full + ".note.html")
        # return html_code
        #
        # return

    @staticmethod
    def server_mode_write_body_htmls():
        pass

    @staticmethod
    def server_mode_get_static_resources(note_book, nodes_dict):
        notes_dest_path_full = note_book.notebook_dest
        files_dest_path_full = os.path.join(notes_dest_path_full, HTML.static_file_dest_path_rel)
        # 准备目标文件夹下的 source 静态文件夹
        if os.path.exists(files_dest_path_full):
            shutil.rmtree(files_dest_path_full)
        os.mkdir(files_dest_path_full)

        # 获取 "/source/all" 和 "/source/server" 下文件夹
        if "-server" in sys.argv:
            static_file_current_mode_path_rel = HTML.static_file_in_lib_path_rel_server_mode
        elif "-local" in sys.argv:
            static_file_current_mode_path_rel = HTML.static_file_in_lib_path_rel_local_mode
        else:
            logging.error("HTML output type is required")
            raise Exception

        static_path_full_all_mode = os.path.join(os.getcwd(), HTML.static_file_in_lib_path_relative_all_mode)
        static_path_current_mode = os.path.join(os.getcwd(), static_file_current_mode_path_rel)

        File.tree_merge_copy(static_path_full_all_mode, files_dest_path_full)
        File.tree_merge_copy(static_path_current_mode, files_dest_path_full)

        HTML.generate_head(note_book, nodes_dict)

        pass

    @staticmethod
    def generate_head(note, note_info_dict):
        # note_dest_path_full = os.path.join(note.note_books_repository, note.note_name)
        # static_file_dest_path_full = os.path.join(note_dest_path_full, HTML.static_file_dest_path_rel)
        #
        # header_html_list = []
        # # Include Remote Libs
        # # 读取Remote的 JavaScript/CSS 库
        # remote_libs_path_full = os.path.join(os.getcwd(), HTML.remote_libs_in_lib_path_relative)
        # remote_libs_file = open(remote_libs_path_full, "r")
        # header_html_list.append(remote_libs_file.read())
        # remote_libs_file.close()
        # Copy to destination
        # 将静态文件文件夹拷贝到系统
        # if not os.path.exists(note_dest_path_full):
        #     os.mkdir(note_dest_path_full)
        #
        # if os.path.exists(static_file_dest_path_full):
        #     shutil.rmtree(static_file_dest_path_full)
        # try:
        #     os.mkdir(static_file_dest_path_full)
        # except FileExistsError:
        #     # 如果笔记的文件夹已经存在
        #     # If note folder already exist
        #     logging.warning("Static files folder already existed.")

        # # 获取 "/source/all" 和 "/source/server" 下文件夹
        # if "-server" in sys.argv:
        #     static_file_current_mode_path_rel = HTML.static_file_in_lib_path_relative_server_mode
        # elif "-local" in sys.argv:
        #     static_file_current_mode_path_rel = HTML.static_file_in_lib_path_relative_local_mode
        # else:
        #     logging.error("HTML output type is required")
        #     raise Exception
        #
        # static_path_full_all_mode = os.path.join(os.getcwd(), HTML.static_file_in_lib_path_relative_all_mode)
        # static_path_current_server_mode = os.path.join(os.getcwd(), static_file_current_mode_path_rel)

        # File.File.tree_merge_copy(static_path_full_all_mode, static_file_dest_path_full)
        # File.File.tree_merge_copy(static_path_current_server_mode, static_file_dest_path_full)

        # # Write mode to script ("-server", "-local")
        # # 将 mode 写入 script ("-server", "-local")
        # if "-server" in sys.argv:
        #     header_html_list.append("<script> let note_mode = \"server\"</script>")
        # elif "-local" in sys.argv:
        #     header_html_list.append("<script> let note_mode = \"local\"</script>")
        # else:
        #     pass
        # Get note info (section id - note_id dictionary)
        # "-server" mode will write note info dict as a js file to /[NOTE_ROOT]/source/js/note_info.js
        # "-local" mode will write note info dict in to <head> tag directly

        # 获取 note info 字典 （类目 id- 笔记id 字典）
        # "-server" 模式将会将 note info 字典作为一个js文件写入到 /[NOTE_ROOT]/source/js/note_info.js
        # "-local" 模式将会将 note info 字典写入到 <head> 标签中
        note_info_script = HTML.note_info_script % json.dumps(note_info_dict)
        if "-server" in sys.argv:
            note_info_script_target_path_full = os.path.join(note.note_root, HTML.note_info_script_target_path_relative)
            note_info_file = open(note_info_script_target_path_full, "w+")
            note_info_file.write(note_info_script)
            note_info_file.close()
        elif "-local" in sys.argv:
            header_html_list.append("<script>%s</script>" % note_info_script)
        else:
            pass
        # 链接 scripts/files 到 <head> 中
        # Link local scripts/files to head
        head_html_dict = {}
        if "-server" in sys.argv:
            head_html_dict = {
                "css": "<link rel=\"stylesheet\" type=\"text/css\" href=\"%s\">",
                "js": "<script src=\"%s\"></script>"
            }
        elif "-local" in sys.argv:
            head_html_dict = {
                "css": "<style>%s</style>",
                "js": "<script>%s</script>"
            }
        else:
            pass
        dir_lists = []
        for element in os.listdir(static_file_dest_path_full):
            if os.path.isdir("%s/%s" % (static_file_dest_path_full, element)):
                dir_lists.append(element)
        for static_type in dir_lists:
            static_dir_path_full = os.path.join(static_file_dest_path_full, static_type)
            for file_name in os.listdir(static_dir_path_full):
                if re.search(r"\.%s$" % static_type, file_name):
                    if "-server" in sys.argv:
                        try:
                            file_path_rel = os.path.join(HTML.static_file_dest_path_rel, static_type, file_name)
                            file_path_rel = "/" + os.path.relpath(file_path_rel)
                            header_html_list.append(head_html_dict[static_type] % file_path_rel)
                        except IndexError:
                            pass
                    elif "-local" in sys.argv:
                        try:
                            script_file = open("%s/%s" % (static_dir_path_full, file_name), "r")
                            script_file_content = script_file.read()
                            header_html_list.append(head_html_dict[static_type] % script_file_content)
                        except IndexError:
                            pass
                    else:
                        pass
        if "-local" in sys.argv:
            shutil.rmtree(static_file_dest_path_full)
        all_header_html = ""
        for header_html in header_html_list:
            all_header_html += header_html + "\n"
        return "<head>\n" + all_header_html + "</head>"

    @staticmethod
    def __check_notebooks_dest_sub_folders(note_books_dest_path_full):
        for sub_folder in Destination.BAIZE_REPO_SUB_FOLDERS_LIST:
            sub_folder = os.path.join(note_books_dest_path_full, sub_folder)
            if not os.path.exists(sub_folder):
                os.mkdir(sub_folder)
