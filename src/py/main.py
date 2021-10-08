import tkinter as tk
from pathlib import Path

import settings
from tkcef import AppManager
from tkcef.webapp import WebView

import ui, jsbind

if __name__ == '__main__':
    settings.load_settings()
    settings.save_settings()
    
    app_man = AppManager()
    app1 = WebView(
        document_path=settings.webpack_dir.joinpath("index.html").absolute().as_uri(),
        js_bindings=jsbind.bindings
    )

    def construct_menubar(root: tk.Tk):
        menubar = tk.Menu(root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open Dev Tools", command=lambda: app1.browser.ShowDevTools())
        filemenu.add_command(label="Full Reload", command=lambda: app1.browser.ReloadIgnoreCache())
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=root.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        
        return menubar
        
    app_man.add_webapp('app1', app1, menubar_builder=construct_menubar)
    
    app_man.mainloop()
    app_man.shutdown()
