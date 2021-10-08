from __future__ import annotations
import os

from colors import *

from . import json_class
from . import anon_func as af


def mkdir_if_missing(dir_path: str):
    if not os.path.isdir(dir_path):
        # os.mkdir(dir_path)
        os.makedirs(dir_path)


def list_contains(p_filter, p_list):
    for x in p_list:
        if p_filter(x):
            return True
    return False


def list_get(p_filter, p_list):
    for x in p_list:
        if p_filter(x):
            return x
    return None


def print_color(fg: str, *args, **kwargs):
    p_list = []
    for i in args:
        p_list.append(color(str(i), fg=fg))

    print(*p_list, **kwargs)


def print_error(*args, **kwargs):
    print_color("red", *args, **kwargs)


def print_warning(*args, **kwargs):
    print_color("yellow", *args, **kwargs)


def yn_prompt(msg: str = "", default=None):
    while True:
        result = input(msg).lower()

        if result == "y":
            return True
        if result == "n":
            return False

        if default is not None:
            print_error("Using default...")
            return default

        print_error("Invalid response. Try again...")




__all__ = (
    "mkdir_if_missing",
    "list_contains",
    "list_get",
    "json_class",
    "af",
    "print_color",
    "print_error",
    "print_warning",
    "yn_prompt",
    "exec_path"
)
