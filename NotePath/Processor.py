from NotePath import BaiZeSys, Destination, Source


class Processor:

    @staticmethod
    def sys_configs_check():
        status = BaiZeSys.BaiZeSys.sys_configs_check()
        if status == BaiZeSys.BaiZeSys.sys_configs_check_no_repo_loc:
            Destination.Destination.initial_notebooks_repository()

    @staticmethod
    def sys_add_a_notebook(note_book_path, note_book_info_dict):
        return BaiZeSys.BaiZeSys.sys_add_a_notebook(note_book_path, note_book_info_dict)

    @staticmethod
    def sys_set_notebooks_info(all_note_books_dict):
        return BaiZeSys.BaiZeSys.sys_set_notebooks_info(all_note_books_dict)

    @staticmethod
    def sys_get_notebooks_info():
        return BaiZeSys.BaiZeSys.sys_get_notebooks_info()

    @staticmethod
    def sys_get_notebooks_paths():
        return BaiZeSys.BaiZeSys.sys_get_notebooks_paths()

    @staticmethod
    def sys_check_notebooks_validation(notebooks_path_list):
        return BaiZeSys.BaiZeSys.sys_check_notebooks_validation(notebooks_path_list)

    @staticmethod
    def sys_get_processing_notebooks_list():
        return BaiZeSys.BaiZeSys.sys_get_processing_notebooks_list()

    @staticmethod
    def sys_get_new_notebook_info(note_book_path_full):
        return BaiZeSys.BaiZeSys.sys_get_new_notebook_info(note_book_path_full)

    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def get_notebooks_destination():
        return Destination.Destination.get_notebooks_destination()

    @staticmethod
    def get_notebook_destination(note_books_dest, notebook_name):
        return Destination.Destination.get_notebook_destination(note_books_dest, notebook_name)

    @staticmethod
    def get_notebooks_repository():
        return Destination.Destination.get_notebooks_repository()

    @staticmethod
    def initial_notebooks_repository():
        return Destination.Destination.initial_notebooks_repository()

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def source_check_section_json(notebook_root):
        return Source.Source.source_check_section_json(notebook_root)

