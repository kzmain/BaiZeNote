section_menu = "<div id=\"section-menu\" class=\"col-sm-2\">\n" \
               "%s\n" \
               "</div>"

note_menu = "<div id=\"note-menu\" class=\"col-sm-2\">\n" \
            "%s\n" \
            "</div>"

burger_icon = """
<svg t="1562723453237" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="3055" width="30" height="30">
<path d="M128 192l768 0 0 128-768 0 0-128Z" p-id="3056">
</path><path d="M128 448l768 0 0 128-768 0 0-128Z" p-id="3057"></path><path d="M128 704l768 0 0 128-768 0 0-128Z" p-id="3058">
</path>
</svg>
"""

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

