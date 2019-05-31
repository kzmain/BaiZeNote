import os
import sys
import datetime
import logging
import json
from Tree.NoteTree import NoteTree
from HTMLs.HTML import HTML
from SVGs.SVG import SVG

section_menu_html = ""
note_menu_dict = {}
file_dict = {}


def main():
    global section_menu_html
    global file_dict
    global note_menu_dict
    if "-i" in sys.argv:
        # Get note book name
        try:
            note_book_name_index = sys.argv.index("-i") + 1
            note_book_name = sys.argv[note_book_name_index]
        except IndexError:
            logging.error("Notebook name is required after \"-i\".")
            return
        # Create or initial exist note
        try:
            # Create Notebook
            os.mkdir(note_book_name)
        except FileExistsError:
            # Already Exist
            logging.error("NoteBook already existed.")
        # write ".notebook.json" to top folder
        write_notebook_json(note_book_name)
        # setup note ".md" and "folder" structure
        note_tree = NoteTree()
        # write ".dir_list.json" and ".file_list.json" to EACH folder
        initial_files_and_sections(".", "%s" % note_book_name, note_tree)
        print(json.dumps(note_menu_dict))
        # for key, value in note_tree.nodes_dict.items():
            # print("%s NodeName: %s" % (key, value.name))
        #     # print("%s ChildNodes: %s" % (key, value.childNodesIds))
        #     # print("%s DirDict: %s" % (key, value.dir_dict))
        #     print("%s FileDict: %s" % (key, note_menu_dict["section%s" % key]))

    section_menu_html = "%s%s%s" % ("\n<div class=\"section-menu\">\n", section_menu_html, "\n</div>")
    note_menu_html = "%s%s" % ("\n<div id=\"note-menu\">\n<span></span>", "\n</div>")
    body_html = "\n<body>\n" + section_menu_html + note_menu_html + "\n</body>"
    head_html = HTML.head.replace("%s", json.dumps(note_menu_dict))
    html = "%s%s" % (head_html, body_html)
    file = open("a.html", "w+")
    file.write(html)
    file.close()


# write ".dir_list.json" and ".file_list.json" to EACH folder
def initial_files_and_sections(parent_path, target_folder, note_tree):
    global section_menu_html
    global file_dict
    global note_menu_dict
    search_uri = "%s/%s" % (parent_path, target_folder)
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
    dir_list = write_dir_or_files_json(dir_list, search_uri, "dir")
    file_list = write_dir_or_files_json(file_list, search_uri, "file")
    current_node_id = note_tree.node_id
    note_tree.add_child_node(search_uri, target_folder)
    # Process sub-folders
    temp_dir_list = dir_list.copy()
    while len(temp_dir_list) > 0:
        note_tree.go_to_node(current_node_id)
        note_tree = initial_files_and_sections(search_uri, temp_dir_list.pop(), note_tree)
        note_tree.go_to_parent_node()
    # Have dir, have/no file(s)
    if len(dir_list) > 0:
        current_node = note_tree.nodes_dict[current_node_id]
        current_node_child_nodes_list = current_node.childNodesIds.copy()
        # current_node_child_nodes_list.reverse()
        child_nodes_html = ""
        for node_id in current_node_child_nodes_list:
            child_nodes_html += note_tree.nodes_dict[node_id].html
        if current_node.name != "Index":
            current_node.html = \
                HTML.sections_span % \
                (current_node_id, current_node_id, SVG.sections_svg, current_node.name, current_node_id,
                 child_nodes_html)
        else:
            current_node.html = child_nodes_html
        # ！！！！！！！回头要check
        note_tree.nodes_dict[current_node_id] = current_node
    # No dir, have file(s)
    elif len(dir_list) == 0 and len(file_list) > 0:
        current_node = note_tree.nodes_dict[current_node_id]
        current_node.html = HTML.no_sections_span % (current_node_id, SVG.no_sections_svg, current_node.name)
        note_tree.nodes_dict[current_node_id] = current_node
    # no dir, no file
    else:
        current_node = note_tree.nodes_dict[current_node_id]
        current_node.html = HTML.no_notes_no_sections_span % (current_node_id, SVG.no_notes_no_sections_svg, current_node.name)
        note_tree.nodes_dict[current_node_id] = current_node
    # node dict
    file_dict[current_node_id] = file_list
    section_menu_html = current_node.html
    # note menu files dict
    note_menu_dict["section%s" % current_node_id] = current_node.file_dict
    return note_tree


# write ".notebook.json" to top folder
def write_notebook_json(note_book_name):
    try:
        note_book_config_json = open("./%s/.notebook.json" % note_book_name, "w+")
        current_datetime = datetime.datetime.now()
        note_book_detail_dict = {"Author": "Kai",
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
def write_dir_or_files_json(file_or_dir_list, search_uri, input_type):
    file_or_dir_dict = {}
    count = 1
    for element in file_or_dir_list:
        file_name_link_dict = {"%s_name" % input_type: element, "%s_uri" % input_type: "%s/%s" % (search_uri, element)}
        file_or_dir_dict[count] = file_name_link_dict
        count += 1
    file = open("%s/.%s_list.json" % (search_uri, input_type), "w+")
    file.write(json.dumps(file_or_dir_dict))
    file.close()
    return file_or_dir_list


if __name__ == '__main__':
    main()
