from __future__ import annotations

import sys, pathlib
from pathlib import Path
import threading
import time
from typing import Type

from cefpython3 import cefpython as cef

from .pyscope import PyScopeManager, BrowserNamespaceWrapper

from .frame import WebFrame

class WebApp:
    browser: cef.PyBrowser = None
    page_code_loader_fn: str = "_load_page_content"

    js_preload_path: str
    js_preload: str
    document_path: str
    
    pyscopemanager: PyScopeManager
    js_bindings: cef.JavascriptBindings

    tk_frame_class: Type[WebFrame]

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
        js_preload_path: str = None,
        js_bind_objects: dict = {},
        tk_frame_class: Type[WebFrame]=WebFrame
    ):
        self.tk_frame: WebFrame = None
        self.tk_frame_class = tk_frame_class
        
        self.js_preload_path = js_preload_path
        if js_preload_path is None:
            self.js_preload_path = Path(__file__).parent.joinpath("js/webapp_preload.js")
        self.js_preload = None
            
        self.js_bind_objects = js_bind_objects
        self.js_bindings = None

        self.document_path = document_path
        self.pyscopemanager = PyScopeManager()
        
        self.app_callbacks = AppCallbacks(self)
        

    def construct_app_webview(
        self, window_info: cef.WindowInfo, client_handlers: list
    ) -> cef.PyBrowser:
        
        self.app_scope = BrowserNamespaceWrapper(self.app_scope_key)
        self.app_scope.set_var('app', self)
        
        self.create_js_bindings()
        cef.PostTask(cef.TID_UI, self.init_browser, window_info, client_handlers)

    def init_browser(self, window_info: cef.WindowInfo, client_handlers: list):
        if self.js_preload is None:
            self.read_js_preload()
        
        self.browser: cef.PyBrowser = cef.CreateBrowserSync(
            window_info
        )
        self.browser.SetJavascriptBindings(self.js_bindings)
        # self.browser.ExecuteJavascript(self.js_preload)

        for i in client_handlers:
            self.browser.SetClientHandler(i)
        
        if self.document_path is not None:
            self.load_page()
    
    def read_js_preload(self):
        js_file = open(self.js_preload_path, "r")
        self.js_preload = js_file.read()
        js_file.close()
            
    def load_page(self, document_path: str = None):

        if document_path is not None:
            self.document_path = document_path

        self.browser.LoadUrl(self.document_path)

    def on_page_loaded(
        self, browser: cef.PyBrowser, frame: cef.PyFrame, http_code: int
    ):
        if self.js_preload is None:
            self.read_js_preload()
            
        browser.ExecuteJavascript(self.js_preload)
        self.pyscopemanager.config_in_browser(browser)
    
    def create_js_bindings(self) -> cef.JavascriptBindings:
        self.js_bindings = cef.JavascriptBindings()
        # print(self.on_app_loaded.__name__)

        self.js_bindings.SetProperty("app_manager_key", self.app_manager_key)
        self.js_bindings.SetProperty("app_scope_key", self.app_scope_key)
        self.js_bindings.SetObject("_pyscopeman", self.pyscopemanager)
        self.js_bindings.SetObject("_pynamespace", BrowserNamespaceWrapper)
        self.js_bindings.SetObject("_app_callbacks", self.app_callbacks)
        self.js_bindings.SetFunction(self.load_page.__name__, self.load_page)
        for key, value in self.js_bind_objects.items():
            self.js_bindings.SetObject(key, value)
        self.js_bindings.Rebind()

        return self.js_bindings
    
    def update(self):
        pass


class AppCallbacks:
    app: WebApp
    def __init__(self, app) -> None:
        self.app = app

    def on_js_title_change(self, new_title: str):
        self.app.tk_frame.set_title(new_title)
