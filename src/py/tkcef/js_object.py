from __future__ import annotations

from pathlib import Path
import traceback
from typing import Any, Callable
import uuid
import threading
import time
import textwrap

from cefpython3 import cefpython as cef

from . import logger

from .js_preload import JsPreloadScript
from util import anon_func as af

# Defining custom exceptions first:

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
    
class JsObjectManagerCallTimeoutException(Exception):
    call: JsObjectManagerCall
    
    def __init__(self, call: JsObjectManagerCall):
        self.call = call
        
    def __str__(self):
        return f"JsObjectManagerCall '{self.call.label}' timed out after waiting {self.call.wait_time}."

# Class definitions:
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
        logger.debug(f"Binding cef.JavascriptCallback '{name}' to JsObjectManager instance...")
        setattr(self, name, callback)

    def ready(self):
        self.is_ready = True
    
    def from_func(self, fn_code, params: dict = {}):
        return JsObject(self, fn_code, params)
    
    def from_id(self, uuid: str) -> JsObject:
        return JsObject(self, None, object_id=uuid)
        
    def from_py(self, obj: Any) -> JsObject:
        if isinstance(obj, JsObject):
            if obj.manager == self:
                return obj
            else:
                return self.from_py(obj.py())
        
        elif isinstance(obj, list) or isinstance(obj, tuple):
            items = [self.from_py(i) for i in obj]
            retVal = self.from_func("return this.get_list(new_item_ids)", {"new_item_ids": items})
            # del items
            return retVal
        
        elif isinstance(obj, dict):
            items = {}
            for key, value in obj.items():
                items[self.from_py(key)] = self.from_py(value)
            
            retVal = self.from_func("return this.get_pairs(new_item_ids)", {"new_item_ids": items})
            return retVal
        
        else:
            return self.from_func("return new_item;", {"new_item": obj})
        
    

class JsObjectManagerCall:
    log_completions: bool = True
    should_raise_timeout_error: bool = False

    label: str
    js_object_id: JsObject
    
    timeout: float
    completed: bool
    timed_out: bool
    start_time: float
    wait_time: float
    result: Any
    error: Any

    # We'll wait 5 seconds by default:
    def __init__(self, js_object: JsObject = None, label: str=None, *, timeout: float = 5.0):
        if js_object is not None:
            self.js_object_id = js_object._object_id
        else:
            self.js_object_id = None
        
        # If timeout is None or <= 0, then we simply wait forever.
        self.timeout = timeout
        self.label = label
        
        self.completed = False
        self.timed_out = False
        self.start_time = None
        self.wait_time = 0
        self.result = None
        self.error = None

    def on_complete(self, result=None, error=None):
        self.result = result
        self.error = error
        self.completed = True
        
        # If start_time is None, we never started waiting:
        if self.log_completions and self.start_time is not None:
            logger.debug(f"JsObjectManagerCall '{self}' completed after waiting {time.monotonic() - self.start_time} sec.")
        
    def wait(self, timeout: float = None):
        if timeout is not None:
            self.timeout = timeout
        
        self.start_time = time.monotonic()
        while not self.completed:
            self.wait_time = time.monotonic() - self.start_time
            # Handle timing out:
            if self.timeout is not None and self.timeout > 0:
                if self.wait_time > self.timeout:
                    self.timed_out = True
                    return

    def __str__(self):
        return f"{self.js_object_id} -> {self.label}"

class JsObject(Callable):    
    _object_id: str
    manager: JsObjectManager
    destroyed: bool

    def __init__(self, manager: JsObjectManager, fn_code: str=None, params: dict = {}, object_id: str = None):
        self.destroyed = False
        
        self._object_id = object_id
        if self._object_id is None:
            self._object_id = str(uuid.uuid4())

        self.manager = manager

        if fn_code is not None:
            call = JsObjectManagerCall(self, 'fadd')
            self.manager.fadd_fn.Call(self._object_id, fn_code, params, call.on_complete)
            call.wait()
            
            # If there's an error during an object's __init__, its __del__ never be called.
            # So if we want to raise anerror in a constructor, we need to manually clear
            # any data that the constructor stored, using self.destroy().
            if call.timed_out:
                self.destroy()
                raise JsObjectManagerCallTimeoutException(call)
            
            if call.error != None:
                self.destroy()
                raise JSObjectException(**call.error)

    def __getitem__(self, key: str) -> JsObject:
        return self.get_attr(key)
    
    def __setitem__(self, key: str, value: Any) -> JsObject:
        return self.set_attr(key, value)

    def __call__(self, *args, **kwargs) -> JsObject:
        if len(kwargs) > 0:
            args += (kwargs,)
        
        return self.call(*args)

    def __del__(self):
        if not self.destroyed:
            self.destroy()
    
    def __str__(self):
        return self._object_id
    
    def destroy(self):
        self.destroyed = True
        # print(f"Destroying {self._object_id}...")
        self.manager.remove_fn.Call(self._object_id, lambda: logger.debug(f"Destroyed JsObject {self._object_id}"))
    
    def access(self, fn_code: str, args={}, obj_param = "obj") -> JsObject:
        call = JsObjectManagerCall(self, "access")
        # Check to see which args are other JsObjects. If any are, we'll let 
        # CEF know to replace those with their actual JavaScript counterparts.
        
        self.manager.access_fn.Call(self._object_id, fn_code, args, obj_param, call.on_complete)
        
        call.wait()
        
        if not self.wait_successful(call):
            return None
            
        return self.manager.from_id(call.result)
    
    def wait_successful(self, call: JsObjectManagerCall):
        if call.timed_out:
            if call.should_raise_timeout_error:
                raise JsObjectManagerCallTimeoutException(call)
            else:
                if call.log_completions:
                    print(f"ERROR: {call} has timed out.")
                return False
                
        if call.error != None:
            raise JSObjectException(**call.error)
        
        return True
        
    def py(self) -> Any:
        call = JsObjectManagerCall(self, "py")
        self.manager.py_fn.Call(self._object_id, call.on_complete)
        
        call.wait()
        
        if not self.wait_successful(call):
            return None
        
        return call.result
    
    def call(self, *args) -> JsObject:
        js_object_args = []
        # Check to see which args are other JsObjects. If any are, we'll let 
        # CEF know to replace those with their actual JavaScript counterparts.
                    
        pass_args = self.manager.from_py(args)
        
        call = JsObjectManagerCall(self, "call")
        # self.manager.call_fn.Call(self._object_id, args, js_object_args, call.on_complete_callback)
        self.manager.call_fn.Call(self._object_id, pass_args, js_object_args, call.on_complete)
        
        # del args_test
        
        call.wait()
        
        if not self.wait_successful(call):
            return None
        
        return self.manager.from_id(call.result)
    
    def call_method(self, method_name: str, *args) -> JsObject:
        js_object_args = []
        
        pass_args = self.manager.from_py(args)
        
        call = JsObjectManagerCall(self, "call_method")
        self.manager.call_method_fn.Call(self._object_id, method_name, pass_args, js_object_args, call.on_complete)
        
        call.wait()
        
        if not self.wait_successful(call):
            return None
        
        return self.manager.from_id(call.result)
    
    def get_attr(self, name: str) -> JsObject:
        call = JsObjectManagerCall(self, "attr")
        self.manager.get_attr_fn.Call(self._object_id, name, call.on_complete)
        
        call.wait()
        
        if not self.wait_successful(call):
            return None
        
        return self.manager.from_id(call.result)
    
    def set_attr(self, name: str, value: Any) -> JsObject:
        is_js_object = False
        
        call = JsObjectManagerCall(self, "set_attr", timeout=None)
        self.manager.set_attr_fn.Call(self._object_id, name, self.manager.from_py(value), is_js_object, call.on_complete)
        
        call.wait()
        
        if not self.wait_successful(call):
            return None
        
        return self.manager.from_id(call.result)
