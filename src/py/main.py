import tkinter as tk
from pathlib import Path

import settings
import tkcef
from tkcef import App, AppManager
from tkcef.webapp import WebApp
from test_app import TestApp

import ui, test_scope

if __name__ == "__main__":
    settings.load_settings()
    settings.save_settings()

    tkcef.expose_namespace(test_scope)

    doc_path = settings.webpack_dir.joinpath("index.html").absolute().as_uri()
    print(f"{doc_path=}")

    app_man = AppManager()
    app1 = TestApp()
    app2 = App()

    app_man.add(app1)
    # app_man.add(app2)

    app_man.mainloop()
    app_man.shutdown()
