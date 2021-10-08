from __future__ import annotations

import pathlib
from pathlib import Path
from types import ModuleType
import random 
from typing import Union
import traceback

from cefpython3 import cefpython as cef

from util import anon_func as af
from . import browser_namespace
from .browser_namespace import BrowserNamespaceWrapper 


class PyScopeManager:
    browser: cef.PyBrowser
    
    js_preload: str
    
    def __init__(self):
        
        js_preload_path = Path(__file__).parent.joinpath("js/pyscope_preload.js")
        
        js_file = open(js_preload_path, 'r')
        self.js_preload = js_file.read()
        js_file.close()
    
    def config_in_browser(self, browser: cef.PyBrowser):
        browser.ExecuteJavascript(self.js_preload)
        
    
    def create(self, call_id: str, complete_callback: cef.JavascriptCallback, kwargs: dict):
        retVal = {
            "result": None,
            "error": None
        }
        try:
            if 'id' in kwargs and kwargs['id'] is not None:
                retVal['result'] = BrowserNamespaceWrapper.create_namespace_if_dne(kwargs['id'])
            else:
                retVal['result'] = BrowserNamespaceWrapper.create_new_namespace()
        except Exception as e:
            retVal['error'] = {
                'message': str(e),
                'name': type(e).__name__,
                'stack': traceback.format_exc()
            }
        
        complete_callback.Call(call_id, retVal);
        
    def destroy(self, call_id: str, complete_callback: cef.JavascriptCallback, kwargs: dict):
        retVal = {
            "result": None,
            "error": None
        }
        try:
            
            retVal['result'] = BrowserNamespaceWrapper.remove_namespace(kwargs['id'])

        except Exception as e:
            retVal['error'] = {
                'message': str(e),
                'name': type(e).__name__,
                'stack': traceback.format_exc()
            }
        
        complete_callback.Call(call_id, retVal);

    def exec(self, call_id: str, complete_callback: cef.JavascriptCallback, kwargs: dict):
        retVal = {
            "result": None,
            "error": None
        }
        try:
            ns = BrowserNamespaceWrapper.namespaces[kwargs['id']]
            retVal['result'] = ns.exec(
                kwargs['code'],
                kwargs['ret_name'],
                kwargs['params'],
            )
        except Exception as e:
            retVal['error'] = {
                'message': str(e),
                'name': type(e).__name__,
                'stack': traceback.format_exc()
            }
        
        complete_callback.Call(call_id, retVal)

    def do_func(self, call_id: str, complete_callback: cef.JavascriptCallback, kwargs: dict):
        retVal = {
            "result": None,
            "error": None
        }
        try:
            ns = BrowserNamespaceWrapper.namespaces[kwargs['id']]
            retVal['result'] = ns.do_func(
                kwargs['code'],
                kwargs['params'],
            )
        except Exception as e:
            retVal['error'] = {
                'message': str(e),
                'name': type(e).__name__,
                'stack': traceback.format_exc()
            }
        
        complete_callback.Call(call_id, retVal)
        
    def make_func(self, call_id: str, complete_callback: cef.JavascriptCallback, kwargs: dict):
        retVal = {
            "result": None,
            "error": None
        }
        try:
            ns = BrowserNamespaceWrapper.namespaces[kwargs['id']]
            retVal['result'] = ns.make_func(
                kwargs['name'],
                kwargs['code'],
                kwargs['params'],
            )
        except Exception as e:
            retVal['error'] = {
                'message': str(e),
                'name': type(e).__name__,
                'stack': traceback.format_exc()
            }
        
        complete_callback.Call(call_id, retVal)
        
    def get_var(self, call_id: str, complete_callback: cef.JavascriptCallback, kwargs: dict):
        retVal = {
            "result": None,
            "error": None
        }
        try:
            ns = BrowserNamespaceWrapper.namespaces[kwargs['id']]
            retVal['result'] = ns.get_var(
                kwargs['name'],
            )
        except Exception as e:
            retVal['error'] = {
                'message': str(e),
                'name': type(e).__name__,
                'stack': traceback.format_exc()
            }
        
        complete_callback.Call(call_id, retVal)
    
    def has_var(self, call_id: str, complete_callback: cef.JavascriptCallback, kwargs: dict):
        retVal = {
            "result": None,
            "error": None
        }
        try:
            ns = BrowserNamespaceWrapper.namespaces[kwargs['id']]
            retVal['result'] = ns.has_var(
                kwargs['name'],
            )
        except Exception as e:
            retVal['error'] = {
                'message': str(e),
                'name': type(e).__name__,
                'stack': traceback.format_exc()
            }
        
        complete_callback.Call(call_id, retVal)
        
    def del_var(self, call_id: str, complete_callback: cef.JavascriptCallback, kwargs: dict):
        retVal = {
            "result": None,
            "error": None
        }
        try:
            ns = BrowserNamespaceWrapper.namespaces[kwargs['id']]
            retVal['result'] = ns.del_var(
                kwargs['name'],
                kwargs['value'],
            )
        except Exception as e:
            retVal['error'] = {
                'message': str(e),
                'name': type(e).__name__,
                'stack': traceback.format_exc()
            }
        
        complete_callback.Call(call_id, retVal)
        
    def set_var(self, call_id: str, complete_callback: cef.JavascriptCallback, kwargs: dict):
        retVal = {
            "result": None,
            "error": None
        }
        try:
            ns = BrowserNamespaceWrapper.namespaces[kwargs['id']]
            retVal['result'] = ns.set_var(
                kwargs['name'],
                kwargs['value'],
            )
        except Exception as e:
            retVal['error'] = {
                'message': str(e),
                'name': type(e).__name__,
                'stack': traceback.format_exc()
            }
        
        complete_callback.Call(call_id, retVal)
        
    def call(self, call_id: str, complete_callback: cef.JavascriptCallback, kwargs: dict):
        retVal = {
            "result": None,
            "error": None
        }
        try:
            ns = BrowserNamespaceWrapper.namespaces[kwargs['id']]
            retVal['result'] = ns.call(
                kwargs['name'],
                kwargs['args'],
                kwargs['kwargs'],
            )
        except Exception as e:
            retVal['error'] = {
                'message': str(e),
                'name': type(e).__name__,
                'stack': traceback.format_exc()
            }
        
        complete_callback.Call(call_id, retVal)
        
    