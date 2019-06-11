import json
import os
import shutil
import sys
from pathlib import Path


class HTML:
    section_menu = "<div id=\"section-menu\" class=\"col-sm-2\">\n" \
                   "%s\n" \
                   "</div>"

    note_menu = "<div id=\"note-menu\" class=\"col-sm-2\">\n" \
                "%s\n" \
                "</div>"

    # 0. %s node id
    # 1. %s node id
    # 2. %s node id
    # 3. %s svg
    # 4. %s current node name
    # 5. %s node id
    # 6. %s sub-folders span
    sections_span = "<span onclick = \"get_note_menu(\'%s\')\" id = \"section-span-%s\">\n" \
                    "  <p data-toggle=\"collapse\" data-target=\"#section%s\">\n" \
                    "    %s\n" \
                    "  </p>\n" \
                    "  <p>%s</p>\n" \
                    "</span>\n" \
                    "<div id=\"section%s\" class=\"collapse\">\n" \
                    "  %s\n" \
                    "</div>"

    # 0. %s node id
    # 1. %s node id
    # 2. %s svg
    # 3. %s current node name
    no_sections_span = "<span onclick = \"get_note_menu(\'%s\')\" id = \"section-span-%s\">\n" \
                       "  <p>\n" \
                       "    %s\n" \
                       "  </p>\n" \
                       "  <p>%s</p>\n" \
                       "</span>\n"

    # 1. %s node id
    # 2. %s node id
    # 3. %s svg
    # 2. %s current node name
    no_notes_no_sections_span = "<span onclick = \"get_note_menu(\'%s\')\" id = \"section-span-%s\">\n" \
                                "  <p>\n" \
                                "    %s\n" \
                                "  </p>\n" \
                                "  <p>%s</p>\n" \
                                "</span>\n"

    note_info_script = "let note_menu_dict = %s"

    # 不同模式下 在库中 对应的静态文件所在地
    static_file_in_lib_path_rel_local_mode = "source/local"
    static_file_in_lib_path_rel_server_mode = "source/server"
    static_file_in_lib_path_relative_all_mode = "source/all"
    static_file_in_lib_path_relative_temp_files = "source/temp"

    remote_libs_in_lib_path_relative = "%s/header.blade.html" % static_file_in_lib_path_relative_temp_files
    # 不同模式下 在目标 对应的静态文件所在地
    dest_path_rel = "source"
    dest_path_rel_note_info_js = "%s/js/note_info.js" % dest_path_rel
    dest_file_name_head_html = "header.blade.html"
    dest_file_name_section_menu_html = "section-menu.blade.html"

    # 📕1. 核心任务
    #   1.1. 生成 "-server"/"-local" 模式的 <head> 部分
    #       1.1.1. "-server" 模式:
    #       Step 1 将 "/source/temp/head.blade.html" 储存的远程 scripts/css 读取，写入到 <head> 中
    #       Step 2 将 "/source/server/" 及 "/source/all/" 下的静态文件拷贝到 "/[note_book_root_folder]/source/"下，如果目标文件夹存在，删除再拷贝
    #       Step 3 输出 note_info_dict 到 "/[note_book_root_folder]/source/js/note_info.js"
    #       Step 4 将所有的网站本地 css/scripts 用链接形式放到 <head> 中
    #       Step 5 将 <head> 最后形成的HTML代码储存到 "/[note_book_root_folder]/source/html/head.blade.html" 下
    #       1.1.2. "-local" 模式:
    #       Step 1 将 "/source/temp/head.blade.html" 储存的远程 scripts/css 读取，加入到 <head> 中
    #       Step 2 将 note_info_dict 转化为 json 加入到 <head> 中
    #       Step 3 将会把 "/source/local/" 及 "/source/all/" 下的静态文件读取到并加入到 <head> 中
    #       Step 4 将 <head> 最后形成的 HTML 代码返回
    # ------------------------------------------------------------------------------------------------------------------
    # 📕1. Core Tasks
    #   1.1. Generate <head> tag part for "-server/-local" mode
    #       1.1.1. "-server" mode:
    #       Step 1 Read remote scripts/css from "/source/temp/head.blade.html", and add it into <head> tag
    #       Step 2 Copy statistic files under "/source/server/" and "/source/all/" to "/[note_book_root_folder]/source/"
    #       , if the target static folder already existed, del it then copy
    #       Step 3 Write note_info_dict to "/[note_book_root_folder]/source/js/note_info.js"
    #       Step 4 Put all local static css/scripts into <head> tag as link format
    #       Step 5 Write final <head> html code to "/[note_book_root_folder]/source/html/head.blade.html"
    #       1.1.2. "-local" mode:
    #       Step 1 Read remote scripts/css from "/source/temp/head.blade.html", and add it into <head> tag
    #       Step 2 Get note_info_dict's json and add it into <head> tag
    #       Step 3 Read static files under "/source/local/" and "/source/all/"  and write into <head> tag
    #       Step 4 Return HTML code back

    @staticmethod
    def get_remote_libs():
        remote_libs_path_full = os.path.join(os.getcwd(), HTML.remote_libs_in_lib_path_relative)
        remote_libs_file = open(remote_libs_path_full, "r")
        remote_libs = remote_libs_file.read()
        remote_libs_file.close()
        return remote_libs

    @staticmethod
    def generate_head(note_book, nodes_dict):
        notes_dest_path_full = note_book.notebook_dest
        files_dest_path_full = os.path.join(notes_dest_path_full, HTML.dest_path_rel)
        header_html_list = [HTML.get_remote_libs()]

        # Include Remote Libs
        # 读取Remote的 JavaScript/CSS 库/ <meta>

        note_info_json = HTML.note_info_script % json.dumps(nodes_dict)
        if "-server" in sys.argv:
            note_info_script_path_full = os.path.join(note_book.notebook_dest,
                                                      HTML.dest_path_rel_note_info_js)
            note_info_file = open(note_info_script_path_full, "w+")
            note_info_file.write(note_info_json)
            note_info_file.close()
        elif "-local" in sys.argv:
            header_html_list.append("<script>%s</script>" % note_info_json)
        else:
            pass

        # 链接 scripts/files 到 <head> 中
        # Link local scripts/files to head
        head_html_dict = {}
        if "-server" in sys.argv:
            head_html_dict = {
                ".css": "<link rel=\"stylesheet\" type=\"text/css\" href=\"%s\">",
                ".js": "<script src=\"%s\"></script>"
            }
        elif "-local" in sys.argv:
            head_html_dict = {
                ".css": "<style>%s</style>",
                ".js": "<script>%s</script>"
            }
        else:
            pass

        for path, dirs, files in os.walk(files_dest_path_full):
            for file in files:
                file_path_rel = "/" + os.path.relpath(os.path.join(path, file), notes_dest_path_full)
                file_type = Path(file_path_rel).suffix
                if "-server" in sys.argv:
                    try:
                        header_html_list.append(head_html_dict[file_type] % file_path_rel)
                    except KeyError:
                        pass
                elif "-local" in sys.argv:
                    try:
                        script_file = open(os.path.join(path, file), "r")
                        script_file_content = script_file.read()
                        script_file.close()
                        header_html_list.append(head_html_dict[file_type] % script_file_content)
                    except KeyError:
                        pass
                else:
                    pass
        if "-local" in sys.argv:
            shutil.rmtree(files_dest_path_full)
        all_header_html = ""
        for header_html in header_html_list:
            all_header_html += header_html + "\n"
        return "<head>\n" + all_header_html + "</head>"

    # 📕1. 核心任务
    #   1.1. 生成 "-server" 模式的 <body> 部分
    #       其中包含的 show_current_note_page 来生成真正的页面
    # ------------------------------------------------------------------------------------------------------------------
    # 📕1. Core Tasks
    #   1.1. Generate <body> tag part for "-server" mode
    #       It includes show_current_note_page to generate real note page
    @staticmethod
    def generate_server_body(section_id, file_id):
        body_html = \
            "<body>\n" \
            "<div class=\"row\">\n" \
            "    <div id=\"section-menu\" class=\"col-sm-2\"></div>\n" \
            "    <div id=\"note-menu\" class=\"col-sm-2\"></div>\n" \
            "    <div id=\"show-note-area\" class=\"col-sm-8\"></div>\n" \
            "</div>\n" \
            "\n" \
            "<script>show_current_note_page(\"%s\", \"%s\")</script>" \
            "</body>" % (section_id, file_id)
        return body_html

    # 📕1. 核心任务
    #   1.1. 生成 "-local" 模式的 <body> 部分
    #       包括完整的 section menu，笔记显示部分将默认显示笔记本的名字
    # ------------------------------------------------------------------------------------------------------------------
    # 📕1. Core Tasks
    #   1.1. Generate <body> tag part for "-local" mode
    #       It includes section menu，show note area will show notebook's name
    @staticmethod
    def generate_local_body(section_menu_content_html, note_name):
        body_html = "\n<body>" \
                    "\n<div class=\"container-fluid\">" \
                    "\n<div class=\"row\">" \
                    "    \n<div id=\"section-menu\" class=\"col-sm-2\">\n%s</div>" \
                    "    \n<div id=\"note-menu\" class=\"col-sm-2\">\n<span></span></div>" \
                    "    \n<div id=\"show-note-area\" class=\"col-sm-8\"><span>%s</span></div>" \
                    "\n</div>" \
                    "\n</div>" \
                    "\n</body>" % (section_menu_content_html, note_name)
        return body_html
