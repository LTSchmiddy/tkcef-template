from __future__ import annotations

from pathlib import Path
import traceback
from typing import Any, Callable
import uuid
import threading
import time
import textwrap

from cefpython3 import cefpython as cef

from .js_preload import JsPreloadScript
from util import anon_func as af


class JsObjectManager:
    is_ready: bool
    browser: cef.PyBrowser

    js_preload: JsPreloadScript

    fadd_fn: cef.JavascriptCallback
    add_fn: cef.JavascriptCallback
    remove_fn: cef.JavascriptCallback
    access_fn: cef.JavascriptCallback
    py_fn: cef.JavascriptCallback
    get_attr_fn: cef.JavascriptCallback
    set_attr_fn: cef.JavascriptCallback
    call_fn: cef.JavascriptCallback
    call_method_fn: cef.JavascriptCallback

    def __init__(self):
        self.is_ready = False
        self.js_preload = JsPreloadScript.new_from_file_path(
            Path(__file__).parent.joinpath("js/jsobject_preload.js")
        )

    def config_in_browser(self, browser: cef.PyBrowser):
        self.js_preload.run(browser)

    def append_callback(self, name: str, callback: cef.JavascriptCallback):
        print(f"Binding '{name}'...")
        setattr(self, name, callback)

    def from_func(self, fn_code):
        return JsObject(self, fn_code)
    
    def from_id(self, uuid: str) -> JsObject:
        return JsObject(self, None, uuid)

    def ready(self):
        self.is_ready = True


class JsCall:
    completed: bool
    result: Any
    error: Any
    
    def __init__(self):
        self.completed = False
        self.result = None
        self.error = None
        
    def on_complete_callback(self, result, error=None):
        self.result = result
        self.error = error
        self.completed = True
        
    def wait(self):
        while not self.completed:
            pass

class JSObjectException(Exception):
    fn_code: str
    name: str
    message: str
    stack: str
    def __init__(self, fn_code: str=None, name: str="", message: str="", stack: str=""):
        self.fn_code = fn_code
        self.name = name
        self.message = message
        self.stack = stack

    def __str__(self):
        retVal = ""
        
        if self.fn_code is not None and self.fn_code.strip() != "":
            indented_fn_code = textwrap.indent(self.fn_code, '\t')
            retVal += f"Error while executing JavaScript code:\n{indented_fn_code}\n\n"
        
        indented_stack = textwrap.indent(self.stack, '\t')
        retVal += f"JavaScript Error:\n{indented_stack}"
        
        return retVal
            
class JsObject(Callable):    
    _object_id: str
    manager: JsObjectManager

    def __init__(self, manager: JsObjectManager, fn_code: str=None, params: dict = {}, object_id: str = None):
        self._object_id = object_id
        if self._object_id is None:
            self._object_id = str(uuid.uuid4())

        self.manager = manager

        if fn_code is not None:
            self.manager.fadd_fn.Call(self._object_id, fn_code, params, lambda: print(f"Created {self._object_id}"))

    def __del__(self):
        self.manager.remove_fn.Call(self._object_id, lambda: print(f"Destroyed {self._object_id}"))
    
    def __str__(self):
        return self._object_id
    
    def __call__(self, *args, **kwargs) -> JsObject:
        if len(kwargs) > 0:
            args += (kwargs,)
        
        return self.call(*args)
    
    def access(self, fn_code: str, args={}, obj_param = "obj") -> JsObject:
        call = JsCall()
        # Check to see which args are other JsObjects. If any are, we'll let 
        # CEF know to replace those with their actual JavaScript counterparts.
        
        self.manager.access_fn.Call(self._object_id, fn_code, args, obj_param, call.on_complete_callback)
        
        call.wait()
        
        if call.error != None:
            raise JSObjectException(**call.error)
            
        return self.manager.from_id(call.result)
    
    def py(self):
        call = JsCall()
        self.manager.py_fn.Call(self._object_id, call.on_complete_callback)
        
        call.wait()
        
        if call.error != None:
            raise JSObjectException(**call.error)
        
        return call.result
    
    def call(self, *args):
        js_object_args = []
        # Check to see which args are other JsObjects. If any are, we'll let 
        # CEF know to replace those with their actual JavaScript counterparts.
        for i in range(0, len(args)):
            if isinstance(args[i], JsObject):
                obj: JsObject = args[i]
                if obj.manager == self.manager:
                    js_object_args.append(i)
                else:
                    args[i] = obj.py()
        
        call = JsCall()
        self.manager.call_fn.Call(self._object_id, args, js_object_args, call.on_complete_callback)
        
        call.wait()
        
        if call.error != None:
            raise JSObjectException(**call.error)
        
        return self.manager.from_id(call.result)
    
    def call_method(self, method_name: str, *args):
        js_object_args = []
        # Check to see which args are other JsObjects. If any are, we'll let 
        # CEF know to replace those with their actual JavaScript counterparts.
        for i in range(0, len(args)):
            if isinstance(args[i], JsObject):
                obj: JsObject = args[i]
                if obj.manager == self.manager:
                    js_object_args.append(i)
                else:
                    args[i] = obj.py()
        
        call = JsCall()
        self.manager.call_method_fn.Call(self._object_id, method_name, args, js_object_args, call.on_complete_callback)
        
        call.wait()
        
        if call.error != None:
            raise JSObjectException(**call.error)
        
        return self.manager.from_id(call.result)
        
    def attr(self, name: str) -> JsObject:
        call = JsCall()
        self.manager.get_attr_fn.Call(self._object_id, name, call.on_complete_callback)
        
        call.wait()
        
        if call.error != None:
            raise JSObjectException(**call.error)
        
        return self.manager.from_id(call.result)
    
    def set_attr(self, name: str, value: Any) -> JsObject:
        is_js_object = False
        
        if isinstance(value, JsObject):
            obj: JsObject = value
            if obj.manager == self.manager:
                is_js_object = True
            else:
                value = obj.py()
        
        call = JsCall()
        self.manager.set_attr_fn.Call(self._object_id, name, value, is_js_object, call.on_complete_callback)
        
        call.wait()
        
        if call.error != None:
            raise JSObjectException(**call.error)
        
        return self.manager.from_id(call.result)
