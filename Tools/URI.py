import os
import re
import uuid


# !!!!!!!!Audio Video
def replace_server_mode_img_uri(html_text, note_folder_resource, image_dict):
    match = re.search(r'(?<=<img src=\")((\.\/)|\.\.\/)+((?!\")(\w|\W))+', html_text)
    while match:
        source_file_path = os.path.abspath(os.path.join(note_folder_resource, match.group(0)))
        file_extension = os.path.splitext(source_file_path)[1]
        dest_file_name = str(uuid.uuid4()) + file_extension
        image_dict[source_file_path] = dest_file_name
        html_text = html_text[:match.start()] + "/source/images/" + dest_file_name + html_text[match.end():]
        match = re.search(r'(?<=<img src=\")((\.\/)|\.\.\/)+((?!\")(\w|\W))+', html_text)
    return html_text


def replace_server_mode_media_uri(html_text, note_folder_resource, media_dict):
    match = re.search(r'(?<=<source src=\")((\.\/)|\.\.\/)+((?!\")(\w|\W))+', html_text)
    while match:
        source_file_path = os.path.abspath(os.path.join(note_folder_resource, match.group(0)))
        file_extension = os.path.splitext(source_file_path)[1]
        dest_file_name = str(uuid.uuid4()) + file_extension
        media_dict[source_file_path] = dest_file_name
        html_text = html_text[:match.start()] + "/source/media/" + dest_file_name + html_text[match.end():]
        match = re.search(r'(?<=<source src=\")((\.\/)|\.\.\/)+((?!\")(\w|\W))+', html_text)
    return html_text


def replace_local_mode_img_uri(html_text, note_folder_resource, image_dict):
    match = re.search(r'(?<=<img src=\")((\.\/)|\.\.\/)+((?!\")(\w|\W))+', html_text)
    dot_replacement = str(uuid.uuid4())
    while match:
        source_file_path = os.path.abspath(os.path.join(note_folder_resource, match.group(0)))
        file_extension = os.path.splitext(source_file_path)[1]
        dest_file_name = str(uuid.uuid4()) + file_extension
        image_dict[source_file_path] = dest_file_name
        # notebook_name = "/" + os.path.basename(notebook_root)
        # rel_path = os.path.relpath(notebook_root, source_file_path).replace(".", dot_replacement)
        html_text = html_text[:match.start()] + dot_replacement + "/source/images/" + dest_file_name + html_text[
                                                                                                       match.end():]
        match = re.search(r'(?<=<img src=\")((\.\/)|\.\.\/)+((?!\")(\w|\W))+', html_text)
    html_text = html_text.replace(dot_replacement, ".")
    return html_text


def replace_local_mode_media_uri(html_text, note_folder_resource, media_dict):
    match = re.search(r'(?<=<source src=\")((\.\/)|\.\.\/)+((?!\")(\w|\W))+', html_text)
    dot_replacement = str(uuid.uuid4())
    while match:
        source_file_path = os.path.abspath(os.path.join(note_folder_resource, match.group(0)))
        file_extension = os.path.splitext(source_file_path)[1]
        dest_file_name = str(uuid.uuid4()) + file_extension
        media_dict[source_file_path] = dest_file_name
        # notebook_name = "/" + os.path.basename(notebook_root)
        # rel_path = os.path.relpath(notebook_root, source_file_path).replace(".", dot_replacement)
        html_text = html_text[:match.start()] + dot_replacement + "/source/media/" + dest_file_name + html_text[
                                                                                                      match.end():]
        match = re.search(r'(?<=<source src=\")((\.\/)|\.\.\/)+((?!\")(\w|\W))+', html_text)
    html_text = html_text.replace(dot_replacement, ".")
    return html_text
