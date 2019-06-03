import json
import os


class HTML:
    section_menu = "<div id=\"section-menu\" class=\"col-sm-2\">\n" \
                   "%s\n" \
                   "</div>"
    note_menu = "<div id=\"note-menu\" class=\"col-sm-2\">\n" \
                "%s\n" \
                "</div>"
    # 0. %s node id
    # 1. %s node id
    # 2. %s svg
    # 3. %s current node name
    # 4. %s node id
    # 5. %s sub-folders span
    sections_span = "<span onclick = \"get_note_menu(\'section%s\')\">\n" \
                    "  <p data-toggle=\"collapse\" data-target=\"#section%s\">\n" \
                    "    %s\n" \
                    "  </p>\n" \
                    "  <p>%s</p>\n" \
                    "</span>\n" \
                    "<div id=\"section%s\" class=\"collapse\">\n" \
                    "  %s\n" \
                    "</div>"
    # 0. %s node id
    # 1. %s svg
    # 2. %s current node name
    no_sections_span = "<span onclick = \"get_note_menu(\'section%s\')\">\n" \
                       "  <p>\n" \
                       "    %s\n" \
                       "  </p>\n" \
                       "  <p>%s</p>\n" \
                       "</span>\n"
    # 1. %s svg
    # 2. %s current node name
    no_notes_no_sections_span = "<span onclick = \"get_note_menu(\'section%s\')\">\n" \
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

    head_server = """<head>

            <script>
            var note_menu_dict = %s

            function test(section_id) {
              let note_menu = document.getElementById("note-menu");
              while (note_menu.firstChild) {
                note_menu.removeChild(note_menu.firstChild)
              }
              let section_files_info = note_menu_dict[section_id];
              for(let key in section_files_info){
                let note_span = document.createElement('span');
                note_span.innerText = section_files_info[key]["html_name"]
                note_span.setAttribute("onclick","readTextFile('"+ section_id+"','" + key + "');");
                note_menu.appendChild(note_span)
              }
            }
            function readTextFile(section_id, note_id)
            {
                    let show_note_area = document.getElementById("show-note-area");
                    // show_note_area.innerHTML = note_menu_dict[section_id][note_id]["html_path_relative"]
                    file_location = note_menu_dict[section_id][note_id]["html_path_relative"]
                    let rawFile = new XMLHttpRequest();
                    rawFile.onreadystatechange = function ()
                    {
                            if(rawFile.readyState === 4)
                            {
                                    if(rawFile.status === 200 || rawFile.status === 0)
                                    {
                                            var allText = rawFile.responseText;
                                            show_note_area.innerHTML = allText
                                    }
                            }
                    }
                    rawFile.open("GET", file_location);
                    rawFile.send(null);
            }
        </script>
    </head>"""

    @staticmethod
    def generate_head(note_info_dict):
        scripts_list = []
        note_info_script = "<script type=\"text/javascript\">\n" \
                           "let note_menu_dict = %s\n" \
                           "</script>" % json.dumps(note_info_dict)

        scripts_list.append(note_info_script)
        # insert /js Javascript Files
        system_javascript_dir = os.getcwd() + "/js"
        system_javascript_list = os.listdir(system_javascript_dir)
        for script_name in system_javascript_list:
            scripts_list.append("<script src=\"%s%s\"></script>" % ("/static_files/js/", script_name))
        all_scripts_html = ""
        for script in scripts_list:
            all_scripts_html += script + "\n"

        # insert /css CSS Files
        css_list = []
        system_css_dir = os.getcwd() + "/css"
        system_css_list = os.listdir(system_css_dir)
        for css_name in system_css_list:
            css_list.append("<link rel=\"stylesheet\" type=\"text/css\" href=\"%s%s\">" % ("/static_files/css/", css_name))
        all_css_html = ""
        for css in css_list:
            all_css_html += css + "\n"

        temp = """
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.0/jquery.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js"></script>
<script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js"></script>"""
        return "<head>\n" + temp+ all_css_html + all_scripts_html  + "</head>"

    @staticmethod
    def generate_body(section_id, md_id):
        body_html = \
            """
<body>

  <div class="row">
<div id="section-menu" class="col-sm-2"><p></p></div>
<div id="note-menu" class="col-sm-2"><p></p></div>
<div id="show-note-area" class="col-sm-8"><p></p></div>
  </div>

<script>show_current_note_page("%s", "%s")</script>
</body>

"""

        body_html = body_html.replace("%s", section_id, 1)
        body_html = body_html.replace("%s", md_id, 1)
        return body_html
