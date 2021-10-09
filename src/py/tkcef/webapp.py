import sys, pathlib
from pathlib import Path
import threading
import time

from cefpython3 import cefpython as cef

from .pyscope import PyScopeManager, BrowserNamespaceWrapper

class WebApp:
    browser: cef.PyBrowser = None
    page_code_loader_fn: str = "_load_page_content"
    
    pyscopemanager: PyScopeManager
    
    js_preload: str
    document_path: str 
    document_code: str 
    
    
    @property
    def app_manager_key(self) -> str:
        return self.tk_frame.app_manager_key


    def __init__(self, *, document_path: str = None, document_code: str = None, js_preload_path: str=None, js_bindings: dict={}, tk_frame=None):
        if js_preload_path is None:
            js_preload_path = Path(__file__).parent.joinpath("js/webapp_preload.js")
        
        js_file = open(js_preload_path, 'r')
        self.js_preload = js_file.read()
        js_file.close()
        
        self.js_bindings = js_bindings
        
        self.document_path = document_path
        self.document_code = document_code
        self.tk_frame: WebFrame = tk_frame
        
        self.pyscopemanager = PyScopeManager()

    def construct_app_webview(
        self,
        window_info: cef.WindowInfo,
        lifespan_handler,
        load_handler,
        focus_handler
    ) -> cef.PyBrowser:  
                      
        js_bindings = self.create_js_bindings()
        
        def _assign_browser(webview: WebApp):
            
            webview.browser: cef.PyBrowser = cef.CreateBrowserSync(
                window_info,
                # settings={
                #     "web_security_disabled": False
                # }
            )
            webview.browser.SetJavascriptBindings(js_bindings)
            webview.browser.ExecuteJavascript(webview.js_preload)
            
            if webview.document_path is not None:
                webview.load_page()
            
            if webview.document_code is not None:
                webview.load_code()
            
            
            webview.browser.SetClientHandler(lifespan_handler)
            webview.browser.SetClientHandler(load_handler)
            webview.browser.SetClientHandler(focus_handler)
            
        
        cef.PostTask(cef.TID_UI, _assign_browser, self)



    def load_page(self, document_path: str = None):
        print("Loading document from path...")
        
        if document_path is not None:
            self.document_path = document_path
        
        # self.browser.LoadUrl("about:blank")
        self.browser.LoadUrl(self.document_path)

    
    def on_page_loaded(self, browser: cef.PyBrowser, frame: cef.PyFrame, http_code: int):
        print("LOAD COMPLETE")
        browser.ExecuteJavascript(self.js_preload)
        self.pyscopemanager.config_in_browser(browser)
        
        if self.document_code is not None:
            self.browser.ExecuteFunction(self.page_code_loader_fn, self.document_code)
        
    
    def load_code(self, document_code: str = None):
        print("Loading document from code...")
        
        if document_code is not None:
            self.document_code = document_code
        
        self.browser.LoadUrl("about:blank")

    
    def create_js_bindings(self) -> cef.JavascriptBindings:
        retVal = cef.JavascriptBindings()
        # print(self.on_app_loaded.__name__)
        
        retVal.SetProperty("app_id", self.app_manager_key)
        retVal.SetObject("_pyscopeman", self.pyscopemanager)
        retVal.SetObject("_pynamespace", BrowserNamespaceWrapper)
        retVal.SetFunction(self.on_app_loaded.__name__, self.on_app_loaded)
        retVal.SetFunction(self.load_page.__name__, self.load_page)
        retVal.SetFunction(self.load_code.__name__, self.load_code)
        for key, value in self.js_bindings.items():
            retVal.SetObject(key, value)
        retVal.Rebind()

        return retVal

    def on_app_loaded(self):
        print("Application loaded...")
 


from .frame import WebFrame