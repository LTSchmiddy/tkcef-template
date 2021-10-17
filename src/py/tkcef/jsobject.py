from __future__ import annotations

from pathlib import Path
import traceback

from cefpython3 import cefpython as cef

from util import anon_func as af

class JsObjectManager:
    browser: cef.PyBrowser

    js_preload: str

    def __init__(self):

        js_preload_path = Path(__file__).parent.joinpath("js/jsobject_preload.js")
        
        js_file = open(js_preload_path, "r")
        self.js_preload = js_file.read()
        js_file.close()
        
    def config_in_browser(self, browser: cef.PyBrowser):
        browser.ExecuteJavascript(self.js_preload)
    
    