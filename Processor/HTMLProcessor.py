import json
import os

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
    def generate_html_header(static_file_dict, sections_dict):
        # 1. 基础头文件标签列表
        # 1. Basic header tags list
        header_html_list = ["<meta charset=\"utf-8\">"]
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
            for section_id, section_dict in sections_dict.items():
                for note_id, note in section_dict.items():
                    html_note_loc_rela = sections_dict[section_id][note_id]["HTML_FILE_REL"] + ".blade.html"
                    html_note_loc_full = os.path.join(Paths.PATH_FULL_NOTEBOOK_DEST, html_note_loc_rela)
                    with open(html_note_loc_full) as file:
                        sections_dict[section_id][note_id]["HTML"] = file.read()
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
        for footer in footer_list:
            footer += footer + "\n"
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
                    script_rel_path = os.path.join(Paths.PATH_RELA_NOTEBOOK_RESOURCE_DEST, script_dict["location"])
                    script_rel_path = "/" + script_rel_path
                    html_code = link_dict[script_dict["type"]] % script_rel_path
                    html_list.append(html_code)
                elif Mode.is_local_mode():
                    script_full_path = os.path.join(Paths.PATH_FULL_NOTEBOOK_RESOURCE_DEST, script_dict["location"])
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
            "   <div class=\"button-menu\">" \
            "       <svg t=\"1562684164543\" class=\"icon\" viewBox=\"0 0 1024 1024\" version=\"1.1\" xmlns=\"http://www.w3.org/2000/svg\" p-id=\"12014\" width=\"30\" height=\"30\">" \
            "           <path d=\"M809.106286 1023.780571H209.627429c-83.748571 0-135.314286-43.373714-135.314286-114.761142V114.980571c0-71.387429 51.565714-114.834286 135.314286-114.834285h599.478857c83.748571 0 135.314286 43.446857 135.314285 114.834285v790.966858c0 74.459429-51.565714 117.833143-135.314285 117.833142zM209.627429 62.244571c-70.875429 0-70.875429 37.229714-70.875429 52.662858v791.04c0 15.506286 0 52.662857 70.948571 52.662857h599.405715c70.875429 0 70.875429-37.156571 70.875428-52.662857V114.980571c0-15.506286 0-52.736-70.948571-52.736H209.700571z\" fill=\"#666666\" p-id=\"12015\">" \
            "           </path><path d=\"M299.885714 1023.780571c-3.218286 0-9.654857 0-12.873143-3.072-29.037714-12.434286-29.037714-12.434286-19.382857-989.476571 0-18.651429 12.946286-31.012571 32.256-31.012571 19.382857 0 32.182857 15.506286 32.182857 31.012571-3.145143 356.717714-6.363429 899.510857 0 952.246857 3.291429 9.289143 0 21.723429-9.581714 31.012572a29.769143 29.769143 0 0 1-22.601143 9.289142zM718.848 310.345143H493.275429c-19.382857 0-32.182857-12.434286-32.182858-31.012572s12.8-31.012571 32.182858-31.012571h225.572571c19.309714 0 32.182857 12.434286 32.182857 31.012571 0 18.651429-12.873143 31.012571-32.182857 31.012572zM718.848 496.493714H493.275429c-19.382857 0-32.182857-12.434286-32.182858-31.012571 0-18.651429 12.8-31.012571 32.182858-31.012572h225.572571c19.309714 0 32.182857 12.434286 32.182857 31.012572s-12.873143 31.012571-32.182857 31.012571z\" fill=\"#666666\" p-id=\"12016\">" \
            "           </path>" \
            "       </svg>" \
            "   </div>" \
            "</div>" \
            "<div class=\"row\">\n" \
            "    <div id=\"section-menu\" class=\"section-menu-fixed col-5 col-sm-2\"></div>\n" \
            "    <div id=\"note-menu\" class=\"note-menu-fixed col-5 col-sm-2\"></div>\n" \
            "    <div id=\"show-note-area\" class=\"col-sm-7\"></div>\n" \
            "</div>\n" \
            "<script>show_current_note_page(\"%s\", \"%s\")</script>\n" \
            "%s\n" \
            "</body>" % (section_id, file_id, html_foot)
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
    def __generate_local_body(html_menu, note_html, html_foot):
        body_html = "\n<body>" \
                    "\n<div class=\"container-fluid\">" \
                    "\n<div class=\"row\">" \
                    "    \n<div id=\"section-menu\" class=\"col-sm-3\">\n%s</div>" \
                    "    \n<div id=\"note-menu\" class=\"col-sm-3\">\n<span></span></div>" \
                    "    \n<div id=\"show-note-area\" class=\"col-sm-6\">%s</div>" \
                    "\n</div>" \
                    "\n</div>" \
                    "\n%s" \
                    "\n</body>" % (html_menu, note_html, html_foot)
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
            body_html = HTMLProcessor.__generate_local_body(html_menu, note_html, html_foot)
        elif Mode.is_server_mode():
            body_html = HTMLProcessor.generate_html_server_body(html_foot, section_id, note_id)
        else:
            return Exception
        return body_html
