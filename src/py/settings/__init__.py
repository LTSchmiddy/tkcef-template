import sys
import os
import json
import pathlib
from pathlib import Path
from typing import Union
from colors import *

src_depth_index = 1

exec_file: Path = None
# determine if application is a script file or frozen exe
if getattr(sys, "frozen", False):
    exec_file = Path(sys.executable)
else:
    exec_file = Path(os.path.abspath(sys.argv[0]))

exec_file_dir: Path = exec_file.parent


root_dir: Path = None
exec_dir: Path = None
rsrc_dir: Path = None

template_dir: Path = None
webpack_dir: Path = None

# If we're executing as the source version, the main .py file  is actually found in the `src` subdirectory
# of the project, and `exec_dir` is changed to reflect that. We'll create `exec_file_dir` in case we actually need the
# unmodified path to that script. Obviously, in build mode, these two values will be the same.
def is_source_version():
    return exec_file.name.endswith(".py")


if is_source_version():
    root_dir = exec_file_dir.parents[src_depth_index]
    exec_dir = root_dir.joinpath("run")
    if not exec_dir.exists():
        os.makedirs(exec_dir, True)

    rsrc_dir = root_dir.joinpath("rsrc")

    template_dir = root_dir.joinpath("src/templates")
    webpack_dir = root_dir.joinpath("dist/webpack/development")


else:
    root_dir = exec_file_dir
    exec_dir = exec_file_dir
    rsrc_dir = exec_file_dir.joinpath("rsrc")

    template_dir = root_dir.joinpath("ui/templates")
    webpack_dir = root_dir.joinpath("ui/webpack")

# print(f"Is Source: {is_source_version()}")
# print(f"Is Build: {is_build_version()}")
# print(f"Exec Dir: {exec_dir}")

settings_file_name = "config.json"
global_settings_path = exec_dir.joinpath(settings_file_name)


def default_settings():
    return {
        "ms_access": {
            "access_path": "C:/Program Files/Microsoft Office/root/Office16/MSACCESS.EXE",
        },
        "remote": {
            "connection": {
                "address": None,
                "port": 22,
                "user": None,
                "pkey_file": None,
            },
            "tunnel": {
                "use_system_ssh": False,
                "forward_config": "5432:localhost:5432",
            },
            "data": {"data-dir": "/opt/database-info"},
        },
        "db": {
            "connection_string": "postgresql://alex:Xxeellaa1@localhost:5433/ms_access"
        },
    }


current = default_settings()


def load_settings(
    path: Union[str, Path] = global_settings_path, settings_dict: dict = current
):
    def recursive_load_list(main: list, loaded: list):
        for i in range(0, max(len(main), len(loaded))):
            # Found in both:
            if i < len(main) and i < len(loaded):
                if isinstance(loaded[i], dict):
                    recursive_load_dict(main[i], loaded[i])
                elif isinstance(loaded[i], list):
                    recursive_load_list(main[i], loaded[i])
                else:
                    main[i] = loaded[i]
            # Found in main only:
            elif i < len(loaded):
                main.append(loaded[i])

    def recursive_load_dict(main: dict, loaded: dict):
        new_update_dict = {}
        for key, value in main.items():
            if not (key in loaded):
                continue
            if isinstance(value, dict):
                recursive_load_dict(value, loaded[key])
            elif isinstance(value, list):
                recursive_load_list(value, loaded[key])
            else:
                new_update_dict[key] = loaded[key]

        # Load settings added to file:
        for key, value in loaded.items():
            if not (key in main):
                new_update_dict[key] = loaded[key]

        main.update(new_update_dict)

    # load preexistent settings file
    if os.path.exists(path) and os.path.isfile(path):
        try:
            imported_settings = json.load(open(path, "r"))
            # current.update(imported_settings)
            recursive_load_dict(settings_dict, imported_settings)
        except json.decoder.JSONDecodeError as e:
            print(color(f"CRITICAL ERROR IN LOADING SETTINGS: {e}", fg="red"))
            print(color("Using default settings...", fg="yellow"))

    # settings file not found
    else:
        save_settings(path, settings_dict)


def save_settings(path: str = global_settings_path, settings_dict: dict = current):
    outfile = open(path, "w")
    json.dump(settings_dict, outfile, indent=4)
    outfile.close()
