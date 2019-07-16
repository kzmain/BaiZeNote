import json
import os

from Processor.Constants import HTML
from Processor.Constants.Paths import Paths
from Tools import Mode


class HTMLProcessor:

    note_info_script = "let note_menu_dict = %s"

    # 不同模式下 在库中 对应的静态文件所在地
    static_rel_local_mode = "source/local"
    static_rel_server_mode = "source/server"
    static_rel_all_mode = "source/all"
    static_rel_remote = "source/remote"
    static_rel_temp = "source/temp"

    remote_libs_in_lib_path_relative = "%s/header.blade.html" % static_rel_remote
    # 不同模式下 在目标 对应的静态文件所在地
    dest_file_name_head_html = "header.blade.html"
    dest_file_name_section_menu_html = "section-menu.blade.html"

    # 📕 核心功能
    # 为多种模式生成头文件
    # ⬇️ 参数
    # static_file_dict: 静态文件字典（包括库文件信息，插入到头文件的脚本信息，插入到尾文件的脚本信息）
    # sections_dict: 包含所有section信息的字典
    # ⬆️ 返回值
    # header: 选择的模式下的header
    # ------------------------------------------------------------------------------------------------------------------
    # 📕 Core function
    # Generate header for multiple mode
    # ⬇️ Parameter:
    # static_file_dict: static files dictionary（include lib files info，header scripts info，footer scripts info）
    # sections_dict: A dictionary includes all sections info
    # ⬆️ Return
    # header: Header for selected mode
    @staticmethod
    def generate_html_header(static_file_dict, sections_dict, notebook_name):
        # 1. 基础头文件标签列表
        # 1. Basic header tags list
        header_html_list = ["<meta charset=\"utf-8\">",
                            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">",
                            "<meta property=\"og:title\" content=\"\" id = \"og-title\">",
                            "<meta property=\"og:description\" content=\"白泽笔记 - 让知识薪火相传\" id = \"og-description\">",
                            "<link rel=\"shortcut icon\" href=\"%s/source/system/favicon.ico\" type=\"image/x-icon\"/>" % ("" if Mode.is_server_mode() else "."),
                            "<script>let notebook_name = \"%s\"</script>" % notebook_name,
                            "<title id = \"title\"></title>",
                            ]
        # 2. 为生成头文件做准备
        #   2.1 配置基础标签形式（链接脚本模式/网页插入脚本模式）
        #   2.1 Set basic header tags list(link script mode/in web script mode)
        link_dict = {
            ".css": "<link rel=\"stylesheet\" type=\"text/css\" href=\"%s\">",
            ".js": "<script src=\"%s\"></script>"
        }
        local_dict = {
            ".css": "<style>%s</style>",
            ".js": "<script>%s</script>"
        }
        #   2.2 准备 note_info.json及main.js
        #   2.2 Prepare note_info.json and main.js
        note_info_json = HTMLProcessor.note_info_script % json.dumps(sections_dict)
        if Mode.is_server_mode():
            # 2.2.1 写入 note_info.json 到本地
            # 2.2.1 Write note_info.json to local file
            with open(Paths.PATH_FULL_NOTEBOOK_INFO_JS_DEST, "w+") as note_info_file:
                note_info_file.write(note_info_json)
            # 2.2.2 `note_info.json` and `main.js` are not in `static_file_dict` so we add them
            # 2.2.2 `note_info.json` 和 `main.js` 不在 `static_file_dict` 内加入他们
            header_html_list.append(link_dict[".js"] % ("/" + Paths.PATH_RELA_NOTEBOOK_INFO_JS_DEST))
            header_html_list.append(link_dict[".js"] % "/source/js/main.js")
            # write section menu

        elif Mode.is_local_mode():
            # 2.2.1 读取本地的 note_name.blade.html 文件到section_dict中
            # 2.2.1 Read local note_name.blade.html files into section_dict
            index_section_id = None
            index_note_id = None
            for section_id, section_dict in sections_dict.items():
                for note_id, note in section_dict.items():
                    html_note_loc_rela = sections_dict[section_id][note_id]["HTML_FILE_REL"] + ".blade.html"
                    html_note_loc_full = os.path.join(Paths.PATH_FULL_NOTEBOOK_DEST, html_note_loc_rela)
                    with open(html_note_loc_full) as file:
                        sections_dict[section_id][note_id]["HTML"] = file.read()
                        # 2.2.2 写入 <title>
                    if index_section_id is None and index_note_id is None:
                        index_section_id = section_id
                        index_note_id = note_id
            note_info_json = HTMLProcessor.note_info_script % json.dumps(sections_dict)
            # 2.2.2 `note_info.json` and `main.js` are not in `static_file_dict` so we add them
            # 2.2.2 `note_info.json` 和 `main.js` 不在 `static_file_dict` 内加入他们
            with open(Paths.PATH_FULL_NOTEBOOK_DEST + "/source/js/main.js") as main_js:
                header_html_list.append(local_dict[".js"] % note_info_json)
                header_html_list.append(local_dict[".js"] % main_js.read())
        else:
            raise Exception
        # 3. 生成头文件脚本列表
        # 3. Generate header file script tags list
        lib_type_list = ["lib", "head"]
        for lib_type in lib_type_list:
            header_html_list = HTMLProcessor.__script_to_html(static_file_dict, lib_type, header_html_list)
        all_header_html = ""
        # 4. 生成头文件
        # 4. Generate header
        for header_html in header_html_list:
            all_header_html += header_html + "\n"
        header = "<head>\n" + all_header_html + "</head>\n"
        return header

    # 📕 核心功能
    # 为多种模式生成尾文件
    # ⬇️ 参数
    # static_file_dict: 静态文件字典（包括库文件信息，插入到头文件的脚本信息，插入到尾文件的脚本信息）
    # ⬆️ 返回值
    # footer: 选择的模式下的header
    # ------------------------------------------------------------------------------------------------------------------
    # 📕 Core function
    # Generate footer for multiple mode
    # ⬇️ Parameter:
    # static_file_dict: static files dictionary（include lib files info，header scripts info，footer scripts info）
    # ⬆️ Return
    # footer: Footer for selected mode
    @staticmethod
    def generate_html_footer(static_file_dict):
        footer = ""
        footer_list = HTMLProcessor.__script_to_html(static_file_dict, "foot", [])
        for element in footer_list:
            footer += element + "\n"
        return footer

    # 📕 核心功能
    # 从系统储存的笔记本中选择要处理的笔记本
    # ⬇️ 参数
    # static_file_dict: 需要打印的元素list
    # lib_type: 静态文件类型
    # ⬆️ 返回值
    # html_list: HTML脚本列表
    # 🎯️ 应用
    # HTMLProcessor.generate_html_header()
    # HTMLProcessor.generate_html_footer()
    # ------------------------------------------------------------------------------------------------------------------
    # 📕 Core function
    # Choose processing notebook(s) from notebook repository(ies) stored in system
    # ⬇️ Parameter:
    # static_file_dict: 静态文件字典
    # lib_type: static file type (e.g. lib, head, foot)
    # ⬆️ Return
    # html_list: HTML Scripts list
    # 🎯Usage:
    # HTMLProcessor.generate_html_header()
    # HTMLProcessor.generate_html_footer()
    @staticmethod
    def __script_to_html(static_file_dict, lib_type, html_list):
        link_dict = {
            ".css": "<link rel=\"stylesheet\" type=\"text/css\" href=\"%s\">",
            ".js": "<script src=\"%s\"></script>"
        }
        local_dict = {
            ".css": "<style>%s</style>",
            ".js": "<script>%s</script>"
        }
        for script_name, script_dict in static_file_dict[lib_type].items():
            if not script_dict["remote"]:
                if Mode.is_server_mode():
                    script_rel_path = os.path.join(Paths.PATH_RELA_NOTEBOOK_SCRIPTS_DEST, script_dict["location"])
                    script_rel_path = "/" + script_rel_path
                    html_code = link_dict[script_dict["type"]] % script_rel_path
                    html_list.append(html_code)
                elif Mode.is_local_mode():
                    script_full_path = os.path.join(Paths.PATH_FULL_NOTEBOOK_SCRIPTS_DEST, script_dict["location"])
                    with open(script_full_path) as script_file:
                        html_list.append(local_dict[script_dict["type"]] % script_file.read())
                else:
                    raise Exception
            else:
                html_list.append(link_dict[script_dict["type"]] % script_dict["location"])
        return html_list

    # 📕 核心功能
    # 为"(-r)server" 模式生成 <body>
    # ⬇️ 参数
    # html_foot: html 脚本文件
    # section_id: 笔记section 的 id
    # file_id: 笔记file 的 id
    # ⬆️ 返回值
    # body_html: HTML <body>
    # ------------------------------------------------------------------------------------------------------------------
    # 📕 Core function
    # Generate <body> for "(-r)server" mode
    # ⬇️ Parameter:
    # html_foot: html footer
    # section_id: note's section's id
    # file_id: note's file's id
    # ⬆️ Return
    # body_html: HTML <body>
    @staticmethod
    def generate_html_server_body(html_foot, section_id, file_id):
        body_html = \
            "<body>\n" \
            "<div class=\"top-nav\">\n" \
            "   <div class=\"button-menu\">\n" \
            "       %s" \
            "   </div>\n" \
            "   <div id = \"banner\">\n" \
            "       <img src = \"/source/system/banner.png\">\n" \
            "   </div>\n" \
            "</div>\n" \
            "<div class=\"row main-container\">\n" \
            "   <div id=\"section-menu\" class=\"section-menu-fixed col-5 col-sm-5 col-md-3 col-lg-2\"></div>\n" \
            "   <div id=\"note-menu\" class=\"note-menu-fixed col-5 col-sm-5 col-md-3 col-lg-2\"></div>\n" \
            "   <div id=\"show-note-area\" class=\"col-md-6 col-lg-8\"></div>\n" \
            "   <div class=\"cover-shadow\"></div>\n" \
            "</div>\n" \
            "<script>show_current_note_page(\"%s\", \"%s\")</script>\n" \
            "%s" \
            "</body>\n" % (HTML.burger_icon, section_id, file_id, html_foot)
        return body_html

    # 📕 核心功能
    # 为"(-r)local" 模式生成 <body>
    # ⬇️ 参数
    # html_menu: html菜单
    # note_html: 显示的note的html
    # html_foot: html尾文件
    # ⬆️ 返回值
    # body_html: HTML <body>
    # 🎯应用:
    # HTMLProcessor.generate_local_html_body()
    # ------------------------------------------------------------------------------------------------------------------
    # 📕 Core function
    # Generate <body> for "(-r)server" mode
    # ⬇️ Parameter:
    # html_menu: html menu
    # note_html: note html for first page
    # html_foot: html footer
    # ⬆️ Return
    # body_html: HTML <body>
    # 🎯Usage:
    # HTMLProcessor.generate_local_html_body()
    @staticmethod
    def __generate_local_body(html_menu, note_html, html_foot, section_id, note_id):
        body_html = "\n<body>" \
                    "<div class=\"top-nav\">\n" \
                    "   <div class=\"button-menu\">\n" \
                    "       %s\n" \
                    "   </div>\n" \
                    "   <div id = \"banner\">\n"\
                    "       <img src = \"./source/system/banner.png\">\n" \
                    "   </div>\n" \
                    "</div>\n" \
                    "<div class=\"row main-container\">\n" \
                    "   <div id=\"section-menu\" class=\"section-menu-fixed col-5 col-sm-5 col-md-3 col-lg-2\">\n%s</div>\n" \
                    "   <div id=\"note-menu\" class=\"note-menu-fixed col-5 col-sm-5 col-md-3 col-lg-2\"></div>\n" \
                    "   <div id=\"show-note-area\" class=\"col-md-6 col-lg-8\">%s</div>\n" \
                    "   <div class=\"cover-shadow\"></div>\n" \
                    "</div>\n" \
                    "<script>get_note_menu(\"%s\", \"%s\")</script>\n" \
                    "%s\n" \
                    "</body>" % (HTML.burger_icon, html_menu, note_html, section_id, note_id, html_foot)
        return body_html

    # 📕 核心功能
    # 为"(-r)local" 模式生成 <body>
    # ⬇️ 参数
    # html_foot: html 脚本文件
    # node_dict: node所有信息的字典
    # section_dict: sections信息字典
    # ⬆️ 返回值
    # body_html: HTML <body>
    # ------------------------------------------------------------------------------------------------------------------
    # 📕 Core function
    # Generate <body> for "(-r)server" mode
    # ⬇️ Parameter:
    # html_foot: html footer
    # node_dict: node's info dict
    # section_dict: sections's info dict
    # ⬆️ Return
    # body_html: HTML <body>
    @staticmethod
    def generate_local_html_body(html_foot, node_dict, section_dict):
        html_menu = node_dict[0].html_section_menu
        section_id = 0
        note_id = 0
        for sec_id, notes_dict in section_dict.items():
            if len(notes_dict) > 0:
                section_id = sec_id
                note_id = str(0)
                break
        if Mode.is_local_mode():
            note_html = section_dict[section_id][note_id]["HTML"]
            body_html = HTMLProcessor.__generate_local_body(html_menu, note_html, html_foot, section_id, note_id)
        elif Mode.is_server_mode():
            body_html = HTMLProcessor.generate_html_server_body(html_foot, section_id, note_id)
        else:
            return Exception
        return body_html
