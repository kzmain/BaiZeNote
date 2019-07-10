import json
import os
import shutil
import sys

from Processor.Constants import Paths, Constants
from Tools import Mode


class HTMLProcessor:
    section_menu = "<div id=\"section-menu\" class=\"col-sm-2\">\n" \
                   "%s\n" \
                   "</div>"

    note_menu = "<div id=\"note-menu\" class=\"col-sm-2\">\n" \
                "%s\n" \
                "</div>"

    # 1. %s node id
    # 2. %s node id
    # 3. %s svg
    # 4. %s current node name
    # 5. %s other spans
    root_sections_span = "<span onclick = \"get_note_menu(\'%s\')\" id = \"section-span-%s\">\n" \
                         "  <p>\n" \
                         "    %s\n" \
                         "  </p>\n" \
                         "  <p>%s</p>\n" \
                         "</span>\n" \
                         "%s\n"
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
    static_rel_local_mode = "source/local"
    static_rel_server_mode = "source/server"
    static_rel_all_mode = "source/all"
    static_rel_remote = "source/remote"
    static_rel_temp = "source/temp"

    remote_libs_in_lib_path_relative = "%s/header.blade.html" % static_rel_remote
    # 不同模式下 在目标 对应的静态文件所在地
    dest_path_rel = "source"
    NOTE_INFO_JS_REL = "%s/js/note_info.js" % dest_path_rel
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

    # @staticmethod
    # def get_remote_libs():
    #     remote_libs_path_full = os.path.join(os.getcwd(), HTMLProcessor.remote_libs_in_lib_path_relative)
    #     remote_libs_file = open(remote_libs_path_full, "r")
    #     remote_libs = remote_libs_file.read()
    #     remote_libs_file.close()
    #     return remote_libs

    @staticmethod
    def generate_head(note_book, nodes_dict, theme_name, theme_mode):
        notes_dest_path_full = note_book.notebook_dest
        files_dest_path_full = os.path.join(notes_dest_path_full, HTMLProcessor.dest_path_rel)
        header_html_list = ["<meta charset=\"utf-8\">"]
        link_dict = {
            ".css": "<link rel=\"stylesheet\" type=\"text/css\" href=\"%s\">",
            ".js": "<script src=\"%s\"></script>"
        }
        local_dict = {
            ".css": "<style>%s</style>",
            ".js": "<script>%s</script>"
        }

        # Include Remote Libs
        # 读取Remote的 JavaScript/CSS 库/ <meta>
        if Mode.is_server_mode():
            note_info_json = HTMLProcessor.note_info_script % json.dumps(nodes_dict)
            note_info_script_path_full = os.path. \
                join(note_book.notebook_dest, HTMLProcessor.NOTE_INFO_JS_REL)
            with open(note_info_script_path_full, "w+") as note_info_file:
                note_info_file.write(note_info_json)
            header_html_list.append(link_dict[".js"] % ("/" + HTMLProcessor.NOTE_INFO_JS_REL))
            header_html_list.append(link_dict[".js"] % "/source/js/main.js")
        elif Mode.is_local_mode():
            for section_id, section_dict in nodes_dict.items():
                for note_id, note in section_dict.items():
                    html_note_loc = os.path. \
                        join(note_book.notebook_dest, nodes_dict[section_id][note_id]["HTML_FILE_REL"] + ".blade.html")
                    with open(html_note_loc) as file:
                        nodes_dict[section_id][note_id]["HTML"] = file.read()
                    os.remove(html_note_loc)
            note_info_json = HTMLProcessor.note_info_script % json.dumps(nodes_dict)
            with open(note_book.notebook_dest + "/source/js/main.js") as main_js:
                header_html_list.append(local_dict[".js"] % note_info_json)
                header_html_list.append(local_dict[".js"] % main_js.read())

            listdir = os.listdir(note_book.notebook_dest)
            listdir.pop(listdir.index("source"))
            for path in listdir:
                shutil.rmtree(os.path.join(note_book.notebook_dest, path))
        else:
            raise Exception

        theme_loc = os.path.join(Paths.PATH_FULL_SYS_LOCATION, "source/themes", theme_name)
        with open(os.path.join(theme_loc, "basic.json")) as basic_json, \
                open(os.path.join(theme_loc, "before_basic.json")) as before_basic_json, \
                open(os.path.join(theme_loc, "after_basic.json")) as after_basic_json:
            other_themes_dicts = [
                json.loads(before_basic_json.read())[theme_mode],
                json.loads(basic_json.read()),
                json.loads(after_basic_json.read())[theme_mode]
            ]

            for theme_dict in other_themes_dicts:
                for script_name, script_dict in theme_dict.items():
                    if not script_dict["remote"]:
                        if Mode.is_server_mode():
                            html_code = link_dict[script_dict["type"]] % ("/source/" + script_dict["location"])
                            header_html_list.append(html_code)
                        elif Mode.is_local_mode():
                            with open(os.path.join(files_dest_path_full, script_dict["location"])) as script_file:
                                header_html_list.append(local_dict[script_dict["type"]] % script_file.read())
                        else:
                            raise Exception
                    else:
                        header_html_list.append(link_dict[script_dict["type"]] % script_dict["location"])
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
            "<div class=\"top-nav\">\n" \
            "<div class=\"button-menu\">" \
            "<svg t=\"1562684164543\" class=\"icon\" viewBox=\"0 0 1024 1024\" version=\"1.1\" xmlns=\"http://www.w3.org/2000/svg\" p-id=\"12014\" width=\"30\" height=\"30\">" \
            "<path d=\"M809.106286 1023.780571H209.627429c-83.748571 0-135.314286-43.373714-135.314286-114.761142V114.980571c0-71.387429 51.565714-114.834286 135.314286-114.834285h599.478857c83.748571 0 135.314286 43.446857 135.314285 114.834285v790.966858c0 74.459429-51.565714 117.833143-135.314285 117.833142zM209.627429 62.244571c-70.875429 0-70.875429 37.229714-70.875429 52.662858v791.04c0 15.506286 0 52.662857 70.948571 52.662857h599.405715c70.875429 0 70.875429-37.156571 70.875428-52.662857V114.980571c0-15.506286 0-52.736-70.948571-52.736H209.700571z\" fill=\"#666666\" p-id=\"12015\">" \
            "</path><path d=\"M299.885714 1023.780571c-3.218286 0-9.654857 0-12.873143-3.072-29.037714-12.434286-29.037714-12.434286-19.382857-989.476571 0-18.651429 12.946286-31.012571 32.256-31.012571 19.382857 0 32.182857 15.506286 32.182857 31.012571-3.145143 356.717714-6.363429 899.510857 0 952.246857 3.291429 9.289143 0 21.723429-9.581714 31.012572a29.769143 29.769143 0 0 1-22.601143 9.289142zM718.848 310.345143H493.275429c-19.382857 0-32.182857-12.434286-32.182858-31.012572s12.8-31.012571 32.182858-31.012571h225.572571c19.309714 0 32.182857 12.434286 32.182857 31.012571 0 18.651429-12.873143 31.012571-32.182857 31.012572zM718.848 496.493714H493.275429c-19.382857 0-32.182857-12.434286-32.182858-31.012571 0-18.651429 12.8-31.012571 32.182858-31.012572h225.572571c19.309714 0 32.182857 12.434286 32.182857 31.012572s-12.873143 31.012571-32.182857 31.012571z\" fill=\"#666666\" p-id=\"12016\">" \
            "</path>" \
            "</svg>" \
            "</div>" \
            "</div>" \
            "<div class=\"row\">\n" \
            "    <div id=\"section-menu\" class=\"section-menu-fixed col-5 col-sm-2\"></div>\n" \
            "    <div id=\"note-menu\" class=\"note-menu-fixed col-5 col-sm-2\"></div>\n" \
            "    <div id=\"show-note-area\" class=\"col-sm-7\"></div>\n" \
            "</div>\n" \
            "<script>show_current_note_page(\"%s\", \"%s\")</script>\n" \
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
                    "    \n<div id=\"section-menu\" class=\"col-sm-3\">\n%s</div>" \
                    "    \n<div id=\"note-menu\" class=\"col-sm-3\">\n<span></span></div>" \
                    "    \n<div id=\"show-note-area\" class=\"col-sm-6\"><span>%s</span></div>" \
                    "\n</div>" \
                    "\n</div>" \
                    "\n</body>" % (section_menu_content_html, note_name)
        return body_html
