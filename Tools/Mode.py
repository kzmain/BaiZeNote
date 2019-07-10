import sys

from Processor.Constants import Constants


def is_local_mode():
    return Constants.REPOSITORY_LOCAL_MODE in sys.argv or Constants.STANDARD_LOCAL_MODE in sys.argv


def is_r_local_mode():
    return Constants.REPOSITORY_LOCAL_MODE in sys.argv


def is_s_local_mode():
    return Constants.STANDARD_LOCAL_MODE in sys.argv


def is_server_mode():
    return Constants.REPOSITORY_SERVER_MODE in sys.argv or Constants.STANDARD_SERVER_MODE in sys.argv


def is_r_server_mode():
    return Constants.REPOSITORY_SERVER_MODE in sys.argv


def is_s_server_mode():
    return Constants.STANDARD_SERVER_MODE in sys.argv
