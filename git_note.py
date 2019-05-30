import os
import re
import sys
import datetime
import logging
import json
from Tree.NoteTree import NoteTree


def main():
    if "-i" in sys.argv:
        # Get note book name
        try:
            note_book_name_index = sys.argv.index("-i") + 1
            note_book_name = sys.argv[note_book_name_index]
        except IndexError:
            logging.error("Notebook name is required after \"-i\".")
            return
        # Create Notebook
        try:
            os.mkdir(note_book_name)
        except FileExistsError:
            logging.error("NoteBook already existed.")
        # Set notebook config
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
        note_tree = NoteTree()
        note_tree = initial_files_and_sections("%s" % note_book_name, note_tree)
        for key, value in note_tree.nodes_dict.items():
            print("%sChildNodes: %s" % (key,value.childNodesIds))
            print("%sDirDict: %s" % (key,value.dir_dict))
            print("%sFileDict: %s" % (key,value.file_dict))


def initial_files_and_sections(search_uri, note_tree):
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
    dir_list = rename_dir_or_files(dir_list, search_uri, "dir")
    file_list = rename_dir_or_files(file_list, search_uri, "file")
    current_node_id = note_tree.node_id
    note_tree.add_child_node(search_uri)
    while len(dir_list) > 0:
        note_tree.go_to_node(current_node_id)
        sub_element_path = "%s/%s" % (search_uri, dir_list.pop())
        note_tree = initial_files_and_sections(sub_element_path, note_tree)
        note_tree.go_to_parent_node()
    return note_tree


def rename_dir_or_files(file_or_dir_list, search_uri, input_type):
    file_or_dir_list.sort()
    file_or_dir_dict = {}
    count = 1
    for element in file_or_dir_list:
        file_or_dir_dict[count] = "%s/%s" % (search_uri, element)
        count += 1
    file = open("%s/.%s_list.json" % (search_uri, input_type), "w+")
    file.write(json.dumps(file_or_dir_dict))
    file.close()
    return file_or_dir_list


if __name__ == '__main__':
    main()
