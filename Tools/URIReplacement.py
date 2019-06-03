import re


# class URIReplacement:

def replace_img_uri(html_text, parent_folder):
    html_text = ___replace___(r"<img( )* src=\"\.\/", html_text, "./", "。%s" % parent_folder)
    html_text = ___replace___(r"<img( )* src=\"\。", html_text, "。", ".")
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
