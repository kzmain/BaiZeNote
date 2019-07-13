import os
from pathlib import Path


class Paths:
    PATH_FULL_SYS_LOCATION = Path(Path(os.path.dirname(__file__)).parent).parent

    PATH_RELA_NOTEBOOKS_RES_LOCATION_JSON = "configs/note_books_resource.json"
    PATH_FULL_NOTEBOOKS_RES_LOCATION_JSON = os.path.join(PATH_FULL_SYS_LOCATION, PATH_RELA_NOTEBOOKS_RES_LOCATION_JSON)

    PATH_RELA_NOTEBOOKS_DEST_LOCATION_JSON = "configs/note_books_destination.json"
    PATH_FULL_NOTEBOOKS_DEST_LOCATION_JSON = os.path.join(PATH_FULL_SYS_LOCATION,
                                                          PATH_RELA_NOTEBOOKS_DEST_LOCATION_JSON)

    PATH_RELA_NOTEBOOKS_THEME_JSON = "configs/note_books_themes.json"
    PATH_FULL_NOTEBOOKS_THEME_JSON = os.path.join(PATH_FULL_SYS_LOCATION, PATH_RELA_NOTEBOOKS_THEME_JSON)

    PATH_FULL_NOTEBOOK_DEST = ""

    PATH_RELA_NOTEBOOK_RESOURCE_DEST = "source"
    PATH_FULL_NOTEBOOK_RESOURCE_DEST = ""

    PATH_FULL_NOTEBOOK_INFO_JS_DEST = ""
    PATH_RELA_NOTEBOOK_INFO_JS_DEST = ""

    PATH_FULL_NOTEBOOK_REPOSITORY = ""

    @staticmethod
    def set_dest_path(notebook_dest, notebook_root):
        Paths.PATH_FULL_NOTEBOOK_DEST = notebook_dest
        Paths.PATH_FULL_NOTEBOOK_RESOURCE_DEST = os.path.join(notebook_dest, Paths.PATH_RELA_NOTEBOOK_RESOURCE_DEST)
        Paths.PATH_FULL_NOTEBOOK_INFO_JS_DEST = "%s/js/note_info.js" % Paths.PATH_FULL_NOTEBOOK_RESOURCE_DEST
        Paths.PATH_RELA_NOTEBOOK_INFO_JS_DEST = "%s/js/note_info.js" % Paths.PATH_RELA_NOTEBOOK_RESOURCE_DEST
        Paths.PATH_FULL_NOTEBOOK_REPOSITORY = notebook_root
