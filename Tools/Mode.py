import sys

from Processor.Constants import SysArgument


def is_local_mode():
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
