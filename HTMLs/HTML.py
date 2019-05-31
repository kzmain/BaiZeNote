class HTML:
    section_menu = "<div class=\"section-menu\">\n" \
                   "%s" \
                   "</div>"
    note_menu = "<div id=\"note-menu\">\n" \
                "%s\n" \
                "</div>"
    # 1. %s node id
    # 2. %s svg
    # 3. %s current node name
    # 4. %s node id
    # 5. %s sub-folders span
    sections_span = "<span onclick = \"test()\">\n" \
                    "  <p data-toggle=\"collapse\" data-target=\"#section%s\">\n" \
                    "    %s\n" \
                    "  </p>\n" \
                    "  <p>%s</p>\n" \
                    "</span>\n" \
                    "<div id=\"section%s\" class=\"collapse\">\n" \
                    "  %s\n" \
                    "</div>"
    # 1. %s svg
    # 2. %s current node name
    no_sections_span = "<span onclick = \"test()\">\n" \
                       "  <p>\n" \
                       "    %s\n" \
                       "  </p>\n" \
                       "  <p>%s</p>\n" \
                       "</span>\n"
    # 1. %s svg
    # 2. %s current node name
    no_notes_no_sections_span = "<span>\n" \
                                "  <p>\n" \
                                "    %s\n" \
                                "  </p>\n" \
                                "  <p>%s</p>\n" \
                                "</span>\n"

    head = """<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.0/jquery.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js"></script>

    <style>
        .section-menu, #note-menu {
            width: 250px; /* Set a width if you like */
            display: inline-block;
            vertical-align: top;
            height: 100%;
            background-color: #eee;
            overflow-y: auto;
        }

        .section-menu span, #note-menu span {
            background-color: #eee; /* Grey background color */
            color: black; /* Black text color */
            display: block; /* Make the links appear below each other */
            padding: 12px; /* Add some padding */
            text-decoration: none; /* Remove underline from links */
        }

        .section-menu span:hover, #note-menu span:hover {
            background-color: #ccc; /* Dark grey background on mouse-over */
        }

        .section-menu span:active, #note-menu span:active {
            background-color: #4CAF50; /* Add a green color to the "active/current" link */
            color: white;
        }
        .section-menu p {
            display: inline;
        }

        .collapse {
            margin-left: 10px;
        }
    </style>

    <script>
        function test() {
            var note_menu = document.getElementById("note-menu")
            while (note_menu.firstChild) {
                note_menu.removeChild(note_menu.firstChild);
            }
            var obj = JSON.parse('{ "name":"John", "age":30, "city":"New York"}');
            for(var key in obj){
                var sectionSpan = document.createElement('span')
                sectionSpan.innerText = obj[key]
                note_menu.appendChild(sectionSpan)
            }
        }
    </script>
</head>"""

    temp = """<div class="section-menu">
        <span><a href="./README.md">Folder 1</a></span>
        <span>Folder 2</span>
        <span>Folder 3</span>
        <span>Folder 4</span>
        <span onclick="test()">
            <p data-toggle="collapse" data-target="#demo">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><path fill="none" d="M0 0h24v24H0V0z"/><path d="M19 18l2 1V3c0-1.1-.9-2-2-2H8.99C7.89 1 7 1.9 7 3h10c1.1 0 2 .9 2 2v13zM15 5H5c-1.1 0-2 .9-2 2v16l7-3 7 3V7c0-1.1-.9-2-2-2z"/></svg>
            </p>
            <p>Folder 5</p>
        </span>
        <div id="demo" class="collapse">
            <span>&nbsp;&nbsp;Link 1</span>
            <span>&nbsp;&nbsp;Link 2</span>
            <span>&nbsp;&nbsp;Link 3</span>
        </div>
    </div>
    <div id="note-menu">
        <span>Folder 1</span>
        <span>Folder 2</span>
        <span>Folder 3</span>
        <span>Folder 4</span>
    </div>"""
