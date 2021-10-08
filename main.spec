# -*- mode: python ; coding: utf-8 -*-

# We can actually use this PyInstaller .spec file to perform additional build 
# tasks before the executable is created. For example, if we call the 
# production webpack compilation here, we ensure it's always up-to-date before 
# including it in the PyInstaller build.

# Even though PyInstaller adds these to the script globals when spec is created, 
# we'll manually import them here to help the code editor along:
from PyInstaller.building.build_main import Analysis
from PyInstaller.building.api import PYZ, EXE, COLLECT
block_cipher = None

import os, subprocess
from pathlib import Path



cef_dir = Path("./venv/Lib/site-packages/cefpython3")

# Graphical Application Definitions:
def run_webpack():    
    return subprocess.run(
        [
            "webpack",
            "--mode", "production",
            "--config", "webpack.config.js",
            "--progress"
        ],
        shell=os.name=='nt'
    )
    
run_webpack()

entry: Path = Path("src/py/main.py")

app = Analysis([entry],
    pathex=['D:\\git-repos\\work\\tkcef-template'],
    binaries=[],
    datas=[
        ("./dist/webpack/production", "./ui/webpack"),
        ("./src/templates", "./ui/templates"),
        ("./src/py/tkcef/js/webapp_preload.js", "./tkcef/js/"),
        ("./src/py/tkcef/js/pyscope_preload.js", "./tkcef/js/"),
        (cef_dir.joinpath("subprocess.exe"), "."),
        (cef_dir.joinpath("locales"), "./locales"),
        (cef_dir.joinpath("swiftshader"), "./swiftshader"),
        (cef_dir.joinpath("*.dat"), "."),
        (cef_dir.joinpath("*.bin"), "."),
        (cef_dir.joinpath("*.pak"), "."),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

app_pyz = PYZ(
    app.pure,
    app.zipped_data,
    cipher=block_cipher
)

app_exe = EXE(
    app_pyz,
    app.scripts, 
    [],
    exclude_binaries=True,
    name='tk_cef_template',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None 
)
app_collection = (
    app_exe,
    app.binaries,
    app.zipfiles,
    app.datas,
)

# Total Build:
args = app_collection

kwargs = dict(
    strip=False,
    upx=True,
    upx_exclude=[],
    name='tk_cef_template'
)

coll = COLLECT(
    *args,
    **kwargs
)
