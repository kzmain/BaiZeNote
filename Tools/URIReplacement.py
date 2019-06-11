import os
import re
import uuid


# class URIReplacement:

def replace_img_uri(html_text, note_folder_resource, image_dict):
    match = re.search(r'(?<=<img src=\")((\.\/)|\.\.\/)+((?!\")(\w|\W))+', html_text)
    while match:
        source_file_path = os.path.abspath(os.path.join(note_folder_resource, match.group(0)))
        file_extension = os.path.splitext(source_file_path)[1]
        dest_file_name = str(uuid.uuid4()) + file_extension
        image_dict[source_file_path] = dest_file_name
        html_text = html_text[:match.start()] + "/source/images/" + dest_file_name + html_text[match.end():]
        match = re.search(r'(?<=<img src=\")((\.\/)|\.\.\/)+((?!\")(\w|\W))+', html_text)
    return html_text


def ___replace___(regx, input_text, replace_target, replace_text):
    # print(input_text)
    body_html_image_match = re.search(regx, input_text)
    while body_html_image_match:
        start_part = input_text[:body_html_image_match.start()]
        replace_part = input_text[body_html_image_match.start():body_html_image_match.end()]
        end_part = input_text[body_html_image_match.end():]
        replace_part = replace_part.replace(replace_target, replace_text, 1)
        input_text = start_part + replace_part + end_part
        body_html_image_match = re.search(regx, input_text)
    return input_text
