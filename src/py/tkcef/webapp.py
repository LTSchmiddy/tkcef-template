from __future__ import annotations

import sys, pathlib
from pathlib import Path
import threading
import time
import traceback
import tkinter as tk
from typing import Callable, Type

from cefpython3 import cefpython as cef

from . import with_uuid4
from .browser_namespace import BrowserNamespaceWrapper
from .pyscope import PyScopeManager
from .js_object import JsObjectManager
from .js_preload import JsPreloadScript
from .frame import WebFrame


class AppCallbacks:
    app: WebApp

    def __init__(self, app) -> None:
        self.app = app

    def on_js_title_change(self, new_title: str):
        self.app.tk_frame.set_title(new_title)


class WebApp:
    browser: cef.PyBrowser = None
    page_code_loader_fn: str = "_load_page_content"

    js_preload_path: str
    js_preload: JsPreloadScript

    document_path: str

    pyscopemanager: PyScopeManager
    jsobjectmanager: JsObjectManager
    js_bindings: cef.JavascriptBindings

    tk_frame_class: Type[WebFrame]
    _first_loop: bool

    @property
    def app_manager_key(self) -> str:
        return self.tk_frame.app_manager_key

    @property
    def app_scope_key(self) -> str:
        return f"SCOPE_{self.app_manager_key}"

    def __init__(
        self,
        *,
        document_path: str = None,
        js_bind_objects: dict = {},
        tk_frame_class: Type[WebFrame] = WebFrame,
    ):
        self._first_loop = True
        self.tk_frame: WebFrame = None
        self.tk_frame_class = tk_frame_class

        js_preload_path = Path(__file__).parent.joinpath("js/webapp_preload.js")
        self.js_preload = JsPreloadScript.new_from_file_path(js_preload_path)

        self.js_bind_objects = js_bind_objects
        self.js_bindings = None

        self.document_path = document_path
        self.pyscopemanager = PyScopeManager()
        self.jsobjectmanager = JsObjectManager()

        self.app_callbacks = AppCallbacks(self)
        self.app_scope = None

    def __del__(self):
        # Destroy the app scope once the app is closed:
        if BrowserNamespaceWrapper.namespace_exists(self.app_scope_key):
            BrowserNamespaceWrapper.remove_namespace(self.app_scope_key)
    
    def construct_app_webview(
        self, window_info: cef.WindowInfo, client_handlers: list
    ) -> cef.PyBrowser:

        BrowserNamespaceWrapper.create_namespace_if_dne(self.app_scope_key)
        self.app_scope = BrowserNamespaceWrapper.namespaces[self.app_scope_key]
        self.app_scope.set_var("app", self)

        self.create_js_bindings()
        cef.PostTask(cef.TID_UI, self.init_browser, window_info, client_handlers)

    def create_js_bindings(self) -> cef.JavascriptBindings:
        self.js_bindings = cef.JavascriptBindings()
        # print(self.on_app_loaded.__name__)

        self.js_bindings.SetProperty("app_manager_key", self.app_manager_key)
        self.js_bindings.SetProperty("app_scope_key", self.app_scope_key)
        self.js_bindings.SetObject("_py_scopeman", self.pyscopemanager)
        self.js_bindings.SetObject("_py_jsobjectman", self.jsobjectmanager)
        self.js_bindings.SetObject("_app_callbacks", self.app_callbacks)
        self.js_bindings.SetFunction(self.load_page.__name__, self.load_page)
        self.js_bindings.SetFunction(with_uuid4.__name__, with_uuid4)
        for key, value in self.js_bind_objects.items():
            self.js_bindings.SetObject(key, value)
        self.additional_js_binds()
        self.js_bindings.Rebind()

        return self.js_bindings

    def init_browser(self, window_info: cef.WindowInfo, client_handlers: list):
        self.browser: cef.PyBrowser = cef.CreateBrowserSync(window_info)
        self.browser.SetJavascriptBindings(self.js_bindings)
        # self.browser.ExecuteJavascript(self.js_preload)

        for i in client_handlers:
            self.browser.SetClientHandler(i)

        if self.document_path is not None:
            self.load_page()

    def load_page(self, document_path: str = None):

        if document_path is not None:
            self.document_path = document_path

        self.browser.LoadUrl(self.document_path)

    def on_page_loaded(
        self, browser: cef.PyBrowser, frame: cef.PyFrame, http_code: int
    ):
        self._first_loop = True
        
        self.js_preload.run(browser)
        self.pyscopemanager.config_in_browser(browser)
        self.jsobjectmanager.config_in_browser(browser)
    
    
    def run_step(self):
        if not self.jsobjectmanager.is_ready:
            return

        # Could we set up a callback with the JsObjectManager? Sure.
        # But this way, we're certain that we're running on the main thread.
        # (I.E, tkinter's update thread.)
        if self._first_loop:
            print("Now running...")
            self.start()
            self._first_loop = False

        self.update()

    # In most cases, these 4 methods are the main ones you want to override:
    def construct_menubar(self, root: tk.Tk) -> tk.Menu:
        menubar = tk.Menu(root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(
            label="Open Developer Tools", command=lambda: self.browser.ShowDevTools()
        )
        filemenu.add_command(
            label="Full Reload", command=lambda: self.browser.ReloadIgnoreCache()
        )
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=root.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        return menubar

    def additional_js_binds(self):
        pass

    def start(self):
        pass

    def update(self):
        pass
