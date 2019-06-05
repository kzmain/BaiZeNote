import json
import os
import re
import shutil
import sys


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
    sections_span = "<span onclick = \"get_note_menu(\'section%s\')\" id = \"section-span-%s\">\n" \
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
    no_sections_span = "<span onclick = \"get_note_menu(\'section%s\')\" id = \"section-span-%s\">\n" \
                       "  <p>\n" \
                       "    %s\n" \
                       "  </p>\n" \
                       "  <p>%s</p>\n" \
                       "</span>\n"
    # 1. %s node id
    # 2. %s node id
    # 3. %s svg
    # 2. %s current node name
    no_notes_no_sections_span = "<span onclick = \"get_note_menu(\'section%s\')\" id = \"section-span-%s\">\n" \
                                "  <p>\n" \
                                "    %s\n" \
                                "  </p>\n" \
                                "  <p>%s</p>\n" \
                                "</span>\n"

    head_local = """<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.0/jquery.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js"></script>

    <style>
        #section-menu, #note-menu {
            /*width: 250px; !* Set a width if you like *!*/
            display: inline-block;
            background-color: #eee;
            /*overflow-y: auto;*/
        }

        #section-menu span, #note-menu span {
            background-color: #eee; /* Grey background color */
            color: black; /* Black text color */
            display: block; /* Make the links appear below each other */
            padding: 12px; /* Add some padding */
            text-decoration: none; /* Remove underline from links */
        }
        #show-note-area{
          /*overflow-y: auto;*/
        }

        #section-menu span:hover, #note-menu span:hover {
            background-color: #ccc; /* Dark grey background on mouse-over */
        }

        #section-menu span:active, #note-menu span:active {
            background-color: #4CAF50; /* Add a green color to the "active/current" link */
            color: white;
        }
        #section-menu p {
            display: inline;
        }

        .collapse {
            margin-left: 10px;
        }

        .col-sm-8, .col-sm-2{
          overflow-y:scroll;
          max-height: 100vh;
          min-height: 100vh;
        }
        img{
            max-width: 60%;
            max-height: 500px;
            height: auto;
            display: block;
            margin-left: auto;
            margin-right: auto;
        }
    </style>

    <script>
        let note_menu_dict = %s
        function test(section_id) {
          let note_menu = document.getElementById("note-menu");
          while (note_menu.firstChild) {
                note_menu.removeChild(note_menu.firstChild)
            }
          let section_files_info = note_menu_dict[section_id];
          for(let key in section_files_info){

            let note_span = document.createElement('span');
            note_span.innerText = section_files_info[key]["html_name"]
            note_span.setAttribute("onclick","note_function('"+ section_id+"','" + key + "');");
            note_menu.appendChild(note_span)
          }
        }
        
        function note_function(section_id, note_id){
          let show_note_area = document.getElementById("show-note-area");
          show_note_area.innerHTML = note_menu_dict[section_id][note_id]["html_code"]
        }
    </script>
</head>"""

    static_file_path_relative = "/source"
    remote_libs_path_relative = "%s/header.blade.html" % static_file_path_relative
    note_info_script_path_relative = "%s/js/note_info.js" % static_file_path_relative
    note_info_script = "let note_menu_dict = %s"

    # Generate "-server" mode's head
    # Generate "-local" mode's head
    @staticmethod
    def generate_head(note, note_info_dict):
        header_html_list = []
        # Include Remote Libs
        # 读取Remote的 JavaScript/CSS 库
        remote_libs_path_full = os.getcwd() + HTML.remote_libs_path_relative
        remote_libs_file = open(remote_libs_path_full, "r")
        header_html_list.append(remote_libs_file.read())
        remote_libs_file.close()
        # Copy to destination (Only -server mode require this operation)
        # 将静态文件文件夹拷贝到系统 (仅 -server 模式需要此操作)
        if "-server" in sys.argv:
            if os.path.exists(note.note_root + HTML.static_file_path_relative):
                shutil.rmtree(note.note_root + HTML.static_file_path_relative)
            shutil.copytree(os.getcwd() + HTML.static_file_path_relative,
                            note.note_root + HTML.static_file_path_relative)
        elif "-local" in sys.argv:
            pass
        else:
            pass
        # Write mode to script ("-server", "-local")
        # 将 mode 写入 script ("-server", "-local")
        if "-server" in sys.argv:
            header_html_list.append("<script> let note_mode = \"server\"</script>")
        elif "-local" in sys.argv:
            header_html_list.append("<script> let note_mode = \"local\"</script>")
        else:
            pass
        # Get note info (section id - note_id dictionary)
        # "-server" mode will write note info dict as a js file to /[NOTE_ROOT]/source/js/note_info.js
        # "-local" mode will write note info dict in to <head> tag directly

        # 获取 note info 字典 （类目 id- 笔记id 字典）
        # "-server" 模式将会将 note info 字典作为一个js文件写入到 /[NOTE_ROOT]/source/js/note_info.js
        # "-local" 模式将会将 note info 字典写入到 <head> 标签中
        note_info_script = HTML.note_info_script % json.dumps(note_info_dict)
        if "-server" in sys.argv:
            note_info_file = open(note.note_root + HTML.note_info_script_path_relative, "w+")
            note_info_file.write(note_info_script)
            note_info_file.close()
            header_html_list.append("<script src=\"%s\"></script>" % HTML.note_info_script_path_relative)
        elif "-local" in sys.argv:
            header_html_list.append("<script>%s</script>" % note_info_script)
        else:
            pass
        # Write and copy static scripts
        head_html_dict = {}
        if "-server" in sys.argv:
            head_html_dict = {
                "css": "<link rel=\"stylesheet\" type=\"text/css\" href=\"%s/%s/%s\">",
                "js": "<script src=\"%s/%s/%s\"></script>"
            }
        elif "-local" in sys.argv:
            head_html_dict = {
                "css": "<style>%s</style>",
                "js": "<script>%s</script>"
            }
        else:
            pass
        dir_lists = []
        for element in os.listdir(os.getcwd() + HTML.static_file_path_relative):
            if os.path.isdir("%s/%s" % (os.getcwd() + HTML.static_file_path_relative, element)):
                dir_lists.append(element)
        for static_type in dir_lists:
            static_dir_path_full = "%s/%s/%s/" % (os.getcwd(), HTML.static_file_path_relative, static_type)
            for file_name in os.listdir(static_dir_path_full):
                if re.search(r"\.%s$" % static_type, file_name):
                    if "-server" in sys.argv:
                        try:
                            header_html_list.append(
                                head_html_dict[static_type] % (HTML.static_file_path_relative, static_type, file_name))
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

        all_header_html = ""
        for header_html in header_html_list:
            all_header_html += header_html + "\n"
        return "<head>\n" + all_header_html + "</head>"

    # Generate "-server" mode's body
    @staticmethod
    def generate_server_body(section_id, md_id):
        body_html = \
            "<body>\n" \
            "<div class=\"row\">\n" \
            "    <div id=\"section-menu\" class=\"col-sm-2\"></div>\n" \
            "    <div id=\"note-menu\" class=\"col-sm-2\"></div>\n" \
            "    <div id=\"show-note-area\" class=\"col-sm-8\"></div>\n" \
            "</div>\n" \
            "\n" \
            "<script>show_current_note_page(\"%s\", \"%s\")</script>" \
            "</body>" % (section_id, md_id)
        return body_html
