from Processor.HTMLProcessor import HTMLProcessor
from Processor.NotebookProcessor import NotebookProcessor
from Processor.ResourceProcessor import ResourceProcessor
from Processor.SysProcessor import SysProcessor
from Processor.DestinationProcessor import DestinationProcessor


class CoreProcessor:
    # SysProcessor -----------------------------------------------------------------------------------------------------
    @staticmethod
    def sys_configs_check():
        SysProcessor.configs_check()

    @staticmethod
    def sys_get_processing_notebooks_list():
        return SysProcessor.get_processing_notebooks_list()

    # ResourceProcessor ------------------------------------------------------------------------------------------------

    @staticmethod
    def res_add_a_notebook(note_book_path, note_book_info_dict):
        return ResourceProcessor.add_resource_notebook(note_book_path, note_book_info_dict)

    @staticmethod
    def res_set_notebooks_info(all_note_books_dict):
        return ResourceProcessor.set_resource_notebook_info(all_note_books_dict)

    @staticmethod
    def res_get_notebooks_info():
        return ResourceProcessor.get_resource_notebooks_info()

    @staticmethod
    def res_get_notebooks_paths():
        return ResourceProcessor.get_resource_notebooks_paths()

    @staticmethod
    def res_check_notebooks_validation(notebooks_path_list):
        return ResourceProcessor.check_resource_notebooks_validation(notebooks_path_list)

    @staticmethod
    def res_get_new_notebook_info(note_book_path_full):
        return ResourceProcessor.get_new_notebook_info(note_book_path_full)

    # DestinationProcessor ---------------------------------------------------------------------------------------------

    @staticmethod
    def get_notebooks_destination():
        return DestinationProcessor.get_notebooks_destination()

    @staticmethod
    def get_notebook_destination(note_books_dest, notebook_name):
        return DestinationProcessor.get_notebook_destination(note_books_dest, notebook_name)

    @staticmethod
    def get_notebooks_repository():
        return DestinationProcessor.get_notebooks_repository()

    @staticmethod
    def initial_notebooks_repository():
        return DestinationProcessor.initial_notebooks_repository()

    @staticmethod
    def prepare_file_writing():
        return DestinationProcessor.prepare_file_writing()

    @staticmethod
    def write_converted_htmls(notebook, nodes_dict):
        # TODO What to do when note status lock / hide tag/reference and so on
        return DestinationProcessor.write_converted_htmls(notebook, nodes_dict)

    # @staticmethod
    # def write_converted_htmls(notebook, notes_dict):
    #     # TODO What to do when note status lock / hide tag/reference and so on
    #     return DestinationProcessor.local_mode_write_converted_htmls(notebook, notes_dict)

    @staticmethod
    def server_mode_write_body_htmls(nodes_dict, html_head, html_foot):
        return DestinationProcessor.server_mode_write_body_htmls(nodes_dict, html_head, html_foot)

    @staticmethod
    def local_mode_write_body_htmls(html_head, html_body):
        return DestinationProcessor.local_mode_write_body_htmls(html_head, html_body)

    @staticmethod
    def write_static_resources(files_dict):
        return DestinationProcessor.write_static_resources(files_dict)

    # NotebookProcessor ------------------------------------------------------------------------------------------------
    @staticmethod
    def notebook_check_section_json(notebook_root):
        return NotebookProcessor.check_section_json(notebook_root)

    # HTMLProcessor ------------------------------------------------------------------------------------------------
    @staticmethod
    def generate_html_header(static_file_dict, nodes_dict):
        return HTMLProcessor.generate_html_header(static_file_dict, nodes_dict)

    @staticmethod
    def generate_html_footer(static_file_dict):
        return HTMLProcessor.generate_html_footer(static_file_dict)

    @staticmethod
    def generate_html_body(html_foot, old_node_dict, new_node_dict):
        return HTMLProcessor.generate_html_body(html_foot, old_node_dict, new_node_dict)
