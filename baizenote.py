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


def main():
    note = Note()
    # ----Create a new notebook mode
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
    # ----Initial a notebook mode
    elif "-i" in sys.argv:
        # 1. Get note book name
        note = Note()
        try:
            note_book_name_index = sys.argv.index("-i") + 1
            note_book_root = sys.argv[note_book_name_index]
            note_book_root = re.sub("\\$", note_book_root, note_book_root)
            # !!!!! Fix it later
            note_book_name = os.path.basename(note_book_root)
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
    else:
        raise Exception
    root_node = note.note_tree.go_to_node(0)
    section_menu_html = HTML.section_menu % root_node.html
    note_menu_html = "%s%s" % ("\n<div id=\"note-menu\" class=\"col-sm-2\">\n<span></span>", "\n</div>")
    html_info_dict = {}
    for key, value in note.note_tree.tree_nodes_dict.items():
        html_info_dict["section%s" % key] = value.md_dict
    if "-local" in sys.argv:
        body_html = "\n<body>" \
                    "\n<div class=\"container-fluid\">" \
                    "\n<div class=\"row\">%s%s" \
                    "<div id=\"show-note-area\" class=\"col-sm-8\"><span>%s</span></div>" \
                    "\n</div>" \
                    "\n</div>" \
                    "\n</body>" % (section_menu_html, note_menu_html, note.note_name)

        head_html = HTML.head_local.replace("%s", json.dumps(html_info_dict))
        file = open(note.note_root + "/index.html", "w+")
        html = "%s%s" % (head_html, body_html)
        file.write(html)
        file.close()
    elif "-server" in sys.argv:
        for root, dirs, files in os.walk("%s" % note.note_root, topdown=False):
            files = [fi for fi in files if fi.endswith(".html")]
            for name in [fi for fi in files if fi.endswith(".html")]:
                file = open(os.path.join(root, name), "r+")
                body_section = file.read()
                file.seek(0)

                body_html = "\n<body>" \
                            "\n<div class=\"container-fluid\">" \
                            "\n<div class=\"row\">%s%s" \
                            "<div id=\"show-note-area\" class=\"col-sm-8\"><span>%s</span></div>" \
                            "\n</div>" \
                            "\n</div>" \
                            "\n</body>" % (section_menu_html, note_menu_html, body_section)
                head_html = HTML.head_server.replace("%s", json.dumps(html_info_dict))
                html = "%s%s" % (head_html, body_html)
                file.write(html)
                file.truncate()
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
def initial_files_and_sections(note, parent_path_relative, target_sub_section):
    if target_sub_section != "":
        target_section_path_relative = "%s%s/" % (parent_path_relative, target_sub_section)
    else:
        target_section_path_relative = parent_path_relative
    target_path_full = note.note_root + target_section_path_relative

    md_section_info_dict = get_md_section_list(note, target_section_path_relative)

    # Current node info
    current_node_id = note.note_tree.node_id
    note.note_tree.add_child_node(target_path_full, target_sub_section, md_section_info_dict)
    current_node = note.note_tree.go_to_node(current_node_id)

    # ------------ 处理 当前node的子node
    dir_list = []
    for key, value in current_node.section_dict.items():
        dir_list.append(value["section_name"])
    while len(dir_list) > 0:
        note.note_tree.go_to_node(current_node_id)
        new_target_sub_folder = dir_list.pop()
        new_parent_folder_relative_uri = target_section_path_relative
        note = initial_files_and_sections(note, new_parent_folder_relative_uri, new_target_sub_folder)
        note.note_tree.go_to_parent_node()

    # ------------ 处理 当前node section menu html
    note.note_tree = process_section_menu(note.note_tree)
    return note


# related to initial_files_and_sections
def get_md_section_list(note, target_section_path_relative):
    target_section_path_full = note.note_root + target_section_path_relative
    # Get Level 1 *Folders* and *Files*
    dir_file_list = os.listdir(target_section_path_full)
    # Split Level 1 "*Folders (sections)* and *.md files*
    section_md_list_dict = {"section": [], "md": []}
    for element in dir_file_list:
        element_path = "%s/%s" % (target_section_path_full, element)
        if os.path.isdir(element_path):
            section_md_list_dict["section"].append(element)
        else:
            if ".md" in element_path:
                section_md_list_dict["md"].append(element)
    # Sort and rename dirs
    section_md_list_dict["section"].sort(reverse=True)
    section_md_list_dict["md"].sort()
    # Get current section's sub section and md files info
    file_dir_dict = {"section_path_relative": target_section_path_relative, "md": {}, "section": {}}
    for inclusion_type, inclusion_list in section_md_list_dict.items():
        count = 1
        inclusion_dict = {}
        for element in inclusion_list:
            element_path_relative = "%s%s" % (target_section_path_relative, element)
            # file_dir_dict[inclusion_type][inclusion_type + str(count)] = \

            element_info_dict = {"%s_name" % inclusion_type: element}
            if inclusion_type == "md":
                html_name = re.sub(r"\.md$", ".html", element)
                html_path_relative = "%s%s" % (target_section_path_relative, html_name)
                html_code_md = md_to_html(note, element_path_relative, target_section_path_relative)
                # md_to_html(note, file_relative_location, folder_path_relative):
                element_info_dict.pop("%s_name" % inclusion_type)
                element_info_dict["html_name"] = html_name
                element_info_dict["html_path_relative"] = html_path_relative
                if "-local" in sys.argv:
                    element_info_dict["html_code"] = html_code_md
            inclusion_dict["%s%s" % (inclusion_type, count)] = element_info_dict
            count += 1
        file_dir_dict[inclusion_type] = inclusion_dict
    return file_dir_dict


# # related to initial_files_and_sections
# # write ".dir_list.json" and ".file_list.json" to current folder
# def get_note_structure_info(md_section_list_dict, note, target_path_relative):
#     file_dir_dict = {"section_path_relative": target_path_relative, "md": {}, "section": {}}
#     for input_type, files in md_section_list_dict.items():
#         count = 1
#         for file_name in files:
#             file_path_relative = ("%s%s" % (target_path_relative, file_name)) if target_path_relative != "/" else (
#                     "%s%s" % (target_path_relative, file_name))
#             file_name_link_dict = \
#                 {
#                     "%s_name" % input_type: file_name,
#                     # "%s_uri" % input_type: file_path_relative
#                 }
#             file_dir_dict[input_type + str(count)] = file_name_link_dict
#             if input_type == "md":
#                 html_path_relative = re.sub(r"\.md$", ".html", file_path_relative)
#                 html_code_md = md_to_html(note, file_path_relative, target_path_relative)
#                 file_dir_dict[input_type + str(count)]["html_path_relative"] = html_path_relative
#                 if "-local" in sys.argv:
#                     file_dir_dict[input_type + str(count)]["html_code"] = html_code_md
#             if input_type == "section":
#                 if "-server" in sys.argv:
#                     file_dir_dict.clear()
#             count += 1
#     # note.add_sections_notes(file_dir_dict)
#     return file_dir_dict


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
    if "-local" in sys.argv:
        html_code = URIReplacement.replace_img_uri(html_code, folder_path_relative)
    local_mode_del_md_html(note.note_root + html_path_relative)
    return html_code


# related to initial_files_and_sections
def local_mode_del_md_html(html_file_location):
    if "-local" in sys.argv:
        os.remove(html_file_location)


def process_section_menu(note_tree):
    current_node = note_tree.current_node
    # Have dir, have/no file(s)
    if len(current_node.section_dict) > 0:

        current_node_child_nodes_list = current_node.childNodesIds.copy()
        child_nodes_html = ""
        for node_id in current_node_child_nodes_list:
            child_nodes_html += note_tree.tree_nodes_dict[node_id].html
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
    elif len(current_node.section_dict) == 0 and len(current_node.md_dict) > 0:
        current_node.html = HTML.no_sections_span % (current_node.nodeId, SVG.no_sections_svg, current_node.name)
    # no dir, no file
    else:
        current_node.html = HTML.no_notes_no_sections_span % \
                            (current_node.nodeId, SVG.no_notes_no_sections_svg, current_node.name)
    note_tree.current_node = current_node
    return note_tree


if __name__ == '__main__':
    main()
