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

from Tools import URIReplacement


# section_menu_html = ""
# note_menu_dict = {}
# file_dict = {}

# -c creation
# -i -initial

def main():
    note = Note()
    # global section_menu_html
    # global file_dict
    # global note_menu_dict
    if "-c" in sys.argv:
        # 1. Get note book name
        try:
            note_book_name_index = sys.argv.index("-c") + 1
            note.note_root_folder = sys.argv[note_book_name_index]
        except IndexError:
            logging.error("Notebook name is required after \"-c\".")
            return
        # 2. Create or initial exist note
        try:
            # Create Notebook
            os.mkdir(note.note_name)
        except FileExistsError:
            # Already Exist
            logging.error("NoteBook already existed.")
    elif "-i" in sys.argv:
        # 1. Get note book name
        note = Note()
        try:
            note_book_name_index = sys.argv.index("-i") + 1
            note_book_root = sys.argv[note_book_name_index]
            note_book_root = re.sub("\\$", note_book_root, note_book_root)
            # !!!!! Fix it later
            note_book_name = ""
            note.note_root = note_book_root
            note.note_name = note_book_name
        except IndexError:
            logging.error("Notebook name is required after \"-c\".")
            return
        # 2. Write notebook setting in ".json" format
        # 2.1 Write ".notebook.json" to top folder
        write_notebook_json(note.note_root)
        # 2.2 Write ".dir_list.json" and ".file_list.json" to EACH folder
        note = initial_files_and_sections(note, "/", "")
        print()
    else:
        raise Exception
    root_node = note.note_tree.go_to_node(0)
    section_menu_html = root_node.html

    section_menu_html = HTML.section_menu % section_menu_html
    note_menu_html = "%s%s" % ("\n<div id=\"note-menu\" class=\"col-sm-2\">\n<span></span>", "\n</div>")

    body_html = "\n<body>" \
                "\n<div class=\"container-fluid\">" \
                "\n<div class=\"row\">" + section_menu_html + note_menu_html + \
                "<div id=\"show-note-area\" class=\"col-sm-8\">" + "<span>To be continue!!!!!!</n>" + "</div>" + \
                "\n</div>" \
                "\n</div>" \
                "\n</body>"
    head_html = HTML.head.replace("%s", json.dumps(note.notebook_dict))
    file = open(note.note_root + "/a.json", "w+")
    file.write(json.dumps(note.notebook_dict))
    file.close()
    file = open(note.note_root + "/index.html", "w+")
    html = "%s%s" % (head_html, body_html)
    file.write(html)
    file.close()


# write ".notebook.json" to top folder
def write_notebook_json(note_book_name):
    try:
        note_book_config_json = open("%s/.notebook.json" % note_book_name, "w+")
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
        # !!!!!!! May be go to update mode
        logging.error("Cannot create notebook configs.")
        return


# write ".dir_list.json" and ".file_list.json" to EACH folder
def initial_files_and_sections(note, parent_path_relative, target_sub_folder):
    if target_sub_folder != "":
        target_path_relative = "%s%s/" % (parent_path_relative, target_sub_folder)
    else:
        target_path_relative = parent_path_relative
    target_path_full = note.note_root + target_path_relative
    file_dir_list_dict = get_file_dir_list(target_path_full)
    write_dir_or_files_json(file_dir_list_dict, note, target_path_relative)

    # Process sub-folders

    # ------------ 处理 当前node的子node
    dir_list = file_dir_list_dict["dir_list"]
    current_node_id = note.note_tree.node_id
    note.note_tree.add_child_node(target_path_full, target_sub_folder)
    while len(dir_list) > 0:
        note.note_tree.go_to_node(current_node_id)
        new_target_sub_folder = dir_list.pop()
        new_parent_folder_relative_uri = target_path_relative
        note = initial_files_and_sections(note, new_parent_folder_relative_uri, new_target_sub_folder)
        note.note_tree.go_to_parent_node()
    note.note_tree.go_to_node(current_node_id)
    # ------------ 处理 当前node section menu html
    note = process_section_menu(note)
    return note


# related to initial_files_and_sections
def get_file_dir_list(target_uri_full):
    dir_file_list = os.listdir(target_uri_full)
    dir_file_list_dict = {"dir_list": [], "file_list": []}
    # Split "Directories" and ".md"
    for element in dir_file_list:
        element_path = "%s/%s" % (target_uri_full, element)
        if os.path.isdir(element_path):
            dir_file_list_dict["dir_list"].append(element)
        else:
            if ".md" in element_path:
                dir_file_list_dict["file_list"].append(element)
    # Sort and rename dirs
    dir_file_list_dict["dir_list"].sort(reverse=True)
    dir_file_list_dict["file_list"].sort()

    # dir_list.reverse()
    return dir_file_list_dict


# related to initial_files_and_sections
# write ".dir_list.json" and ".file_list.json" to current folder
def write_dir_or_files_json(file_dir_list_dict, note, target_path_relative):
    file_dir_dict = {"section_path_relative": target_path_relative}
    for input_type, files in file_dir_list_dict.items():
        count = 1
        input_type = input_type.replace("_list", "")
        for file_name in files:
            file_path_relative = ("%s%s" % (target_path_relative, file_name)) if target_path_relative != "/" else (
                    "%s%s" % (target_path_relative, file_name))
            file_name_link_dict = \
                {
                    "%s_name" % input_type: file_name,
                    "%s_uri" % input_type: file_path_relative
                }
            file_dir_dict[input_type + str(count)] = file_name_link_dict
            if input_type == "file":
                html_path_relative = re.sub(r"\.md$", ".html", file_path_relative)
                html_code_md = md_to_html(note, file_path_relative, target_path_relative)
                file_dir_dict[input_type + str(count)]["html_path_relative"] = html_path_relative
                file_dir_dict[input_type + str(count)]["html_code"] = html_code_md
            count += 1
    note.add_sections_notes(file_dir_dict)
    file = open("%s/.node_list.json" % (note.note_root + target_path_relative), "w+")
    file.write(json.dumps(file_dir_dict))
    file.close()


# related to initial_files_and_sections
# e.g.
def md_to_html(note, file_relative_location, folder_path_relative):
    # Process .md files
    md.process(["-f", "%s%s" % (note.note_root, file_relative_location)])
    # Open local html files
    # Read .md file's .html
    html_path_relative = re.sub(r"\.md$", ".html", file_relative_location)
    html_file = open(note.note_root + html_path_relative, "r")
    html_code = html_file.read()
    html_file.close()
    html_code = URIReplacement.replace_img_uri(html_code, folder_path_relative)
    local_mode_del_md_html(note.note_root + html_path_relative)
    return html_code


# related to initial_files_and_sections
def local_mode_del_md_html(html_file_location):
    if "-local" in sys.argv:
        os.remove(html_file_location)


def process_section_menu(note):
    current_node = note.note_tree.current_node
    # Have dir, have/no file(s)
    if len(current_node.dir_dict) > 0:

        current_node_child_nodes_list = current_node.childNodesIds.copy()
        child_nodes_html = ""
        for node_id in current_node_child_nodes_list:
            child_nodes_html += note.note_tree.tree_nodes_dict[node_id].html
        if current_node.name != "Index":
            current_node.html = \
                HTML.sections_span % \
                (current_node.nodeId,
                 current_node.nodeId,
                 SVG.sections_svg,
                 current_node.name,
                 current_node.nodeId,
                 child_nodes_html)
        else:
            current_node.html = child_nodes_html
    # No dir, have file(s)
    elif len(current_node.dir_dict) == 0 and len(current_node.file_dict) > 0:
        current_node.html = HTML.no_sections_span % (current_node.nodeId, SVG.no_sections_svg, current_node.name)
    # no dir, no file
    else:
        current_node.html = HTML.no_notes_no_sections_span % \
                            (current_node.nodeId, SVG.no_notes_no_sections_svg, current_node.name)
    note.note_tree.current_node = current_node
    return note


if __name__ == '__main__':
    main()
