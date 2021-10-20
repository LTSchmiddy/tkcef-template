import tkinter as tk
from pathlib import Path

import settings
import tkcef
from tkcef import AppManager
from tkcef.webapp import WebApp

import ui, jsbind, test_scope

if __name__ == "__main__":
    settings.load_settings()
    settings.save_settings()

    print(tkcef.expose_namespace(test_scope))

    app_man = AppManager()
    app1 = WebApp(
        document_path=settings.webpack_dir.joinpath("index.html").absolute().as_uri(),
        js_bind_objects=jsbind.bindings,
    )

    app_man.add_webapp("app1", app1)

    app_man.mainloop()
    # app_man.shutdown()
