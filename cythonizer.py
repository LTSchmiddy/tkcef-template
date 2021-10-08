import sys, os, pathlib, shutil, glob
from pathlib import Path

from distutils.core import setup, Extension
from typing import Callable
from Cython.Build import *
from Cython.Compiler.Errors import CompileError

platform_extension = 'pyd' if os.name == "nt"  else "so"

def compile_cython(classname: str, path: Path, delete_c: False, delete_py: False):
    retVal = None

    new_extension = Extension(classname, [str(path)])
    old_args = sys.argv
    # sys.argv = [old_args[0], 'build_ext'] #, '--inplace']
    # sys.argv = [old_args[0], 'build_ext', '--inplace']
    sys.argv = [old_args[0], "build_ext", f"--build-lib={path.parent}"]
    try:
        result = setup(
            name=classname,
            ext_modules=cythonize(
                new_extension, compiler_directives={"language_level": "3"}
            ),
        )

        retVal = result
    except Exception as e:
        print(e)
    finally:
        sys.argv = old_args

    glob_str = (
        f"{os.path.splitext(path.with_name(classname))[0]}.*.{platform_extension}"
    )
    out_search = glob.glob(glob_str)

    print(glob_str)
    print(out_search)

    if len(out_search) != 1:
        print(f"FATAL ERROR: Could not determine output file for {path}")
        return retVal

    out_file = Path(out_search[0])

    os.rename(out_file, path.with_suffix("." + platform_extension))

    if delete_c and path.with_suffix(".c").exists():
        os.remove(path.with_suffix(".c"))

    if delete_py and path.exists():
        os.remove(path)

    return retVal

    
def handle_file(match: Path, output_dir: Path, cythonize_filter: Callable = lambda x: True):
    out_path = output_dir.joinpath(match)
    
    print(f"\tCopying to {out_path}")
    os.makedirs(out_path.parent, exist_ok=True)
    shutil.copyfile(match, out_path)
    
    if cythonize_filter(out_path):
        classname = out_path.stem
        if classname == "__init__":
            classname = out_path.parent.name
        
        compile_cython(classname, out_path, True, True)