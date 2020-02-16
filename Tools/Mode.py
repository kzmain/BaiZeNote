import sys

from Constants import SysArgument


def is_local_mode():
    print(sys.argv)
    return SysArgument.REPOSITORY_LOCAL_MODE in sys.argv or SysArgument.STANDARD_LOCAL_MODE in sys.argv


def is_r_local_mode():
    return SysArgument.REPOSITORY_LOCAL_MODE in sys.argv


def is_s_local_mode():
    return SysArgument.STANDARD_LOCAL_MODE in sys.argv


def is_server_mode():
    return SysArgument.REPOSITORY_SERVER_MODE in sys.argv or SysArgument.STANDARD_SERVER_MODE in sys.argv


def is_r_server_mode():
    return SysArgument.REPOSITORY_SERVER_MODE in sys.argv


def is_s_server_mode():
    return SysArgument.STANDARD_SERVER_MODE in sys.argv


def static_file_belong_to_current_mode(script_dict):
    if "target" in script_dict.keys():
        if script_dict["target"] == "local" and is_server_mode():
            return False
        elif script_dict["target"] == "server" and is_local_mode():
            return False
    return True
