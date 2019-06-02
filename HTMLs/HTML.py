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
    sections_span = "<span onclick = \"test(\'section%s\')\">\n" \
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
    no_sections_span = "<span onclick = \"test(\'section%s\')\">\n" \
                       "  <p>\n" \
                       "    %s\n" \
                       "  </p>\n" \
                       "  <p>%s</p>\n" \
                       "</span>\n"
    # 1. %s svg
    # 2. %s current node name
    no_notes_no_sections_span = "<span onclick = \"test(\'section%s\')\">\n" \
                                "  <p>\n" \
                                "    %s\n" \
                                "  </p>\n" \
                                "  <p>%s</p>\n" \
                                "</span>\n"

    head = """<head>
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
    </style>

    <script>
        var note_menu_dict = %s
        function test(section_id) {
            var note_menu = document.getElementById("note-menu")
            while (note_menu.firstChild) {
                note_menu.removeChild(note_menu.firstChild)
            }
            var section_files_info = note_menu_dict[section_id]
            for(var key in section_files_info){
                if(!(key.includes("file"))){
                    continue
                }
                var note_span = document.createElement('span')
                note_span.innerText = section_files_info[key]["file_name"]
                note_span.setAttribute("onclick","note_function('"+ section_id+"','" + key + "');");
                note_menu.appendChild(note_span)
            }
        }
        function note_function(section_id, note_id){
          var show_note_area = document.getElementById("show-note-area")
          show_note_area.innerHTML = note_menu_dict[section_id][note_id]["html_code"]
        }
    </script>
</head>"""
