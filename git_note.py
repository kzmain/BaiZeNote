import os
import re
import sys
import datetime
import logging
import json

from Note import Note
from HTMLs.HTML import HTML
from SVGs.SVG import SVG
import emarkdown.markdown as md

section_menu_html = ""
note_menu_dict = {}
file_dict = {}


def main():
    note = Note()
    global section_menu_html
    global file_dict
    global note_menu_dict
    if "-i" in sys.argv:
        # Get note book name
        try:
            note_book_name_index = sys.argv.index("-i") + 1
            note.note_name = sys.argv[note_book_name_index]
            note.note_root_folder = "./%s/" % note.note_name
        except IndexError:
            logging.error("Notebook name is required after \"-i\".")
            return
        # Create or initial exist note
        try:
            # Create Notebook
            os.mkdir(note.note_name)
        except FileExistsError:
            # Already Exist
            logging.error("NoteBook already existed.")
        # write ".notebook.json" to top folder
        write_notebook_json(note.note_name)
        # write ".dir_list.json" and ".file_list.json" to EACH folder
        initial_files_and_sections(note, "", "")
    else:
        return Exception
    section_menu_html = HTML.section_menu % section_menu_html
    note_menu_html = "%s%s" % ("\n<div id=\"note-menu\" class=\"col-sm-2\">\n<span></span>", "\n</div>")
    for root, dirs, files in os.walk("./%s" % note.note_name, topdown=False):
        files = [fi for fi in files if fi.endswith(".html")]
        for name in [fi for fi in files if fi.endswith(".html")]:
            file = open(os.path.join(root, name), "r+")
            body_section = file.read()
            file.seek(0)

            body_html = "\n<body>" \
                        "\n<div class=\"container-fluid\">" \
                        "\n<div class=\"row\">" + section_menu_html + note_menu_html + \
                        "<div id=\"show-note-area\" class=\"col-sm-8\">" + body_section + "</div>" + \
                        "\n</div>" \
                        "\n</div>" \
                        "\n</body>"
            head_html = HTML.head.replace("%s", json.dumps(note_menu_dict))
            html = "%s%s" % (head_html, body_html)
            file.write(html)
            file.truncate()
            file.close()


# write ".dir_list.json" and ".file_list.json" to EACH folder
def initial_files_and_sections(note, parent_folder_relative_uri, target_sub_folder):
    global section_menu_html
    global file_dict
    global note_menu_dict
    if parent_folder_relative_uri != "":
        parent_path = "%s%s" % (note.note_root_folder, parent_folder_relative_uri)
    else:
        parent_path = note.note_root_folder
    if target_sub_folder != "":
        search_uri = "%s%s/" % (parent_path, target_sub_folder)
    else:
        search_uri = note.note_root_folder
    dir_file_list = os.listdir(search_uri)
    dir_list = []
    file_list = []
    # Split "Directories" and ".md"
    for element in dir_file_list:
        element_path = "%s/%s" % (search_uri, element)
        if os.path.isdir(element_path):
            dir_list.append(element)
        else:
            if ".md" in element_path:
                file_list.append(element)
    # Sort and rename dirs
    dir_list.sort()
    file_list.sort()
    dir_list.reverse()
    dir_list = write_dir_or_files_json("dir", dir_list, search_uri, parent_folder_relative_uri + target_sub_folder)
    file_list = write_dir_or_files_json("file", file_list, search_uri, parent_folder_relative_uri + target_sub_folder)
    current_node_id = note.note_tree.node_id
    note.note_tree.add_child_node(search_uri, target_sub_folder)
    # Process sub-folders
    temp_dir_list = dir_list.copy()

    new_parent_folder_relative_uri = search_uri.replace(note.note_root_folder, "")
    while len(temp_dir_list) > 0:
        note.note_tree.go_to_node(current_node_id)
        new_target_sub_folder = temp_dir_list.pop()
        note_tree = initial_files_and_sections(note, new_parent_folder_relative_uri, new_target_sub_folder)
        note_tree.go_to_parent_node()
    # Have dir, have/no file(s)
    if len(dir_list) > 0:
        current_node = note.note_tree.nodes_dict[current_node_id]
        current_node_child_nodes_list = current_node.childNodesIds.copy()
        # current_node_child_nodes_list.reverse()
        child_nodes_html = ""
        for node_id in current_node_child_nodes_list:
            child_nodes_html += note.note_tree.nodes_dict[node_id].html
        if current_node.name != "Index":
            current_node.html = \
                HTML.sections_span % \
                (current_node_id, current_node_id, SVG.sections_svg, current_node.name, current_node_id,
                 child_nodes_html)
        else:
            current_node.html = child_nodes_html
        # ！！！！！！！回头要check
        note.note_tree.nodes_dict[current_node_id] = current_node
    # No dir, have file(s)
    elif len(dir_list) == 0 and len(file_list) > 0:
        current_node = note.note_tree.nodes_dict[current_node_id]
        current_node.html = HTML.no_sections_span % (current_node_id, SVG.no_sections_svg, current_node.name)
        note.note_tree.nodes_dict[current_node_id] = current_node
    # no dir, no file
    else:
        current_node = note.note_tree.nodes_dict[current_node_id]
        current_node.html = HTML.no_notes_no_sections_span % \
                            (current_node_id, SVG.no_notes_no_sections_svg, current_node.name)
        note.note_tree.nodes_dict[current_node_id] = current_node
    # node dict
    file_dict[current_node_id] = file_list
    section_menu_html = current_node.html
    # note menu files dict
    note_menu_dict["section%s" % current_node_id] = current_node.file_dict
    return note.note_tree


# write ".notebook.json" to top folder
def write_notebook_json(note_book_name):
    try:
        note_book_config_json = open("./%s/.notebook.json" % note_book_name, "w+")
        current_datetime = datetime.datetime.now()
        note_book_detail_dict = \
            {"Author": "Kai",
             "Date": "%s-%s-%s" %
                     (current_datetime.year,
                      current_datetime.month,
                      current_datetime.day),
             "Note_Name": note_book_name,
             "Time": "%s:%s:%s:%s" %
                     (current_datetime.hour,
                      current_datetime.minute,
                      current_datetime.second,
                      current_datetime.microsecond)
             }
        note_book_config_json.write(json.dumps(note_book_detail_dict))
        note_book_config_json.close()
    except FileExistsError:
        logging.error("Cannot create notebook configs.")
        return


# write ".dir_list.json" and ".file_list.json" to current folder
def write_dir_or_files_json(input_type, file_or_dir_list, search_uri, parent_folder):
    a= parent_folder
    file_or_dir_dict = {}
    count = 1
    for element in file_or_dir_list:
        temp = element.replace(".md", ".html")

        file_name_link_dict = \
            {
                "%s_name" % input_type: element, "%s_uri" % input_type: "/%s/%s" % (parent_folder, temp)}
        file_or_dir_dict[count] = file_name_link_dict
        if input_type == "file":
            md.process(["-f", "%s/%s" % (search_uri, element)])
            md_html_file = open("%s/%s" % (search_uri, temp), "r")
            # file_or_dir_dict[count]["html"] = md_html_file.read()
            middle_html = md_html_file.read()
            md_html_file.close()
            # Replace html ./ href
            body_html_image_match = re.search(r"<img( )* src=\".\/\w", middle_html)
            while body_html_image_match:
                start_part = middle_html[:body_html_image_match.start()]
                replace_part = middle_html[body_html_image_match.start():body_html_image_match.end() - 1]
                end_part = middle_html[body_html_image_match.end() - 1:]
                replace_part = replace_part.replace("./", "/%s/" % parent_folder, 1)
                middle_html = start_part + replace_part + end_part
                body_html_image_match = re.search(r"<img( )* src=\".\/\w", middle_html)
            file_or_dir_dict[count]["html"] = middle_html
        count += 1
    file = open("%s/.%s_list.json" % (search_uri, input_type), "w+")
    file.write(json.dumps(file_or_dir_dict))
    file.close()
    return file_or_dir_list


if __name__ == '__main__':
    main()
