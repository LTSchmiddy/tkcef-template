from __future__ import annotations

from pathlib import Path
import traceback
from typing import Any, Callable, Union, get_type_hints
import uuid
import threading
import time
import textwrap

from cefpython3 import cefpython as cef

from . import logger

from .js_preload import JsPreloadScript
from util import anon_func as af

DEBUGGING = True


# Defining custom exceptions first:


class JSObjectException(Exception):
    fn_code: str
    name: str
    message: str
    stack: str

    def __init__(
        self, fn_code: str = None, name: str = "", message: str = "", stack: str = ""
    ):
        self.fn_code = fn_code
        self.name = name
        self.message = message
        self.stack = stack

    def __str__(self):
        retVal = ""

        if self.fn_code is not None and self.fn_code.strip() != "":
            indented_fn_code = textwrap.indent(self.fn_code, "\t")
            retVal += f"Error while executing JavaScript code:\n{indented_fn_code}\n\n"

        indented_stack = textwrap.indent(self.stack, "\t")
        retVal += f"JavaScript Error:\n{indented_stack}"

        return retVal


class JsObjectManagerCallTimeoutException(Exception):
    call: JsObjectManagerCall

    def __init__(self, call: JsObjectManagerCall):
        self.call = call

    def __str__(self):
        return f"JsObjectManagerCall '{self.call.label}' timed out after waiting {self.call.wait_time}."
    
class JsObjectManagerCallDestroyedException(Exception):
    call: JsObjectManagerCall

    def __init__(self, call: JsObjectManagerCall):
        self.call = call

    def __str__(self):
        return f"The JsObject for '{self.call.label}' was destroyed, but you're still trying to access it."


# ==== Class definitions: ====
class JsObjectManager:
    is_ready: bool
    js_bindings: cef.JavascriptBindings

    js_preload: JsPreloadScript

    fadd_fn: cef.JavascriptCallback
    add_fn: cef.JavascriptCallback
    remove_fn: cef.JavascriptCallback
    access_fn: cef.JavascriptCallback
    py_fn: cef.JavascriptCallback
    auto_convert_fn: cef.JavascriptCallback
    get_type_fn: cef.JavascriptCallback
    get_attr_fn: cef.JavascriptCallback
    set_attr_fn: cef.JavascriptCallback
    has_attr_fn: cef.JavascriptCallback
    del_attr_fn: cef.JavascriptCallback
    call_fn: cef.JavascriptCallback
    call_method_fn: cef.JavascriptCallback

    def __init__(self, js_bindings: cef.JavascriptBindings):
        self.js_bindings = js_bindings
        self.is_ready = False
        self.js_preload = JsPreloadScript.new_from_file_path(
            Path(__file__).parent.joinpath("js/jsobject_preload.js")
        )

    def config_in_browser(self, browser: cef.PyBrowser):
        self.js_preload.run(browser)

    def append_callback(self, name: str, callback: cef.JavascriptCallback):
        logger.debug(
            f"Binding cef.JavascriptCallback '{name}' to JsObjectManager instance..."
        )
        setattr(self, name, callback)

    def can_cef_convert(self, obj: Any) -> bool:
        try:
            # Manually specifying 'is True' because some of the other return options are truthy.
            if self.js_bindings.IsValueAllowedRecursively(obj) is True:
                return True
        
        # There seems to be an issue with IsValueAllowedRecursively and JsObject's tendency
        # to convert itself to a string when necessary. Fortunately, this is also a 'False' scenario.
        except AttributeError as e:
            pass
        
        return False

    def ready(self):
        self.is_ready = True

    def get_js_type(self, item) -> str:
        return self.from_py(item).get_js_type()
    
    
    def from_func(self, fn_code, params: dict = {}, convert_args: bool = True):
        return JsObject(manager=self, fn_code=fn_code, args=params, convert_args=convert_args)

    def from_id(self, uuid: str, new_type: type[JsObject] = None):
        if new_type is None:
            new_type = JsObject
            
        return new_type(manager=self, object_id=uuid)

    # The 'skip_cef_converts' param results in remarkably fewer calls between Python and JS.
    # Hopefully, it will result in considerably improved performance.
    def from_py(self, obj: Any, skip_cef_converts: bool = True, store_cef_converts: bool = True) -> JsObject:
        # If CEF can perform the conversion on it's own, that will be much faster:
        if skip_cef_converts and self.can_cef_convert(obj):
            
            # print(f"CEF will convert {obj=} by itself...")
            
            if store_cef_converts:
                return self.from_func("return new_item;", {"new_item": obj}, False)
            
            else:
                # If we're not storing CEF converts, then we just get the original value back:
                return obj;
        
        # print(f"Tkcef will convert {obj=} manually...")
        
        if isinstance(obj, cef.JavascriptCallback):
            return self.from_py(obj.Call, skip_cef_converts, store_cef_converts)

        elif isinstance(obj, JsObject):
            if obj.manager == self:
                return obj
            else:
                return self.from_py(obj.py(), skip_cef_converts, store_cef_converts)

        elif isinstance(obj, list) or isinstance(obj, tuple):
            pairs = [self.from_py(i, skip_cef_converts, False) for i in obj]
            
            retVal = None
            if skip_cef_converts:
                converts = [i for i in range(0, len(pairs)) if issubclass(type(pairs[i]), JsObject)]
                
                retVal = self.from_func(
                    "return this.convert_list_items_in_place(new_item_ids, converts);", {"new_item_ids": pairs, "converts": converts}, False
                )
            else:
                retVal = self.from_func(
                    "return this.get_list(new_item_ids)", {"new_item_ids": pairs}, False
                )
            # del items
            return retVal

        elif isinstance(obj, dict):
            
            retVal = None
            # if False: pass
            if skip_cef_converts:
                # This should ensure the keys and values stay in the same order:
                items = obj.items()
                keys = [self.from_py(i[0], skip_cef_converts, False) for i in items]
                values = [self.from_py(i[1], skip_cef_converts, False) for i in items]
                
                # I suppose I could have converted the key and value lists by running them  each through 
                # from_py again. But, I'm trying to reduce the number of js exchanges per method call.
                # In simpler cases, that strategy would result in MORE js calls, not fewer.
                convert_keys = [i for i in range(0, len(keys)) if issubclass(type(keys[i]), JsObject)]
                convert_values = [i for i in range(0, len(values)) if issubclass(type(values[i]), JsObject)]
                
                retVal = self.from_func(
                    "return this.convert_in_place_and_make_pairs_from_lists(keys, convert_keys, values, convert_values);",
                    {
                        "keys": keys,
                        "convert_keys": convert_keys,
                        "values": values,
                        "convert_values": convert_values
                    },
                    False
                )
            else:
                pairs = {}
                for key, value in obj.items():
                    pairs[self.from_py(key)] = self.from_py(value)

                retVal = self.from_func(
                    "return this.get_pairs(new_item_ids)", {"new_item_ids": pairs}, False
                )
            return retVal
        
        # When using skip_cef_converts, if the item was convertable, it should have been added by now.
        # But if not, check and handle that here.
        elif (not skip_cef_converts) and self.can_cef_convert(obj):
            return self.from_func("return new_item;", {"new_item": obj}, False)
        else:
            # If something can't be converted, just make it undefined.
            # Having this as a failsafe oughta improve stability somewhat.
            return self.from_func("return undefined;", {}, False)
            

class JsObjectManagerCall:
    log_completions: bool = DEBUGGING
    should_raise_timeout_error: bool = not DEBUGGING

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
    def __init__(
        self, js_object: JsObject = None, label: str = None, *, timeout: float = 5.0
    ):
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
        
    @property
    def value(self):
        return self.py()

    def on_complete(self, result=None, error=None):
        self.result = result
        self.error = error
        self.completed = True

        # If start_time is None, we never started waiting:
        if self.log_completions and self.start_time is not None:
            logger.debug(
                f"JsObjectManagerCall '{self}' completed after waiting {time.monotonic() - self.start_time} sec."
            )

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
    REPR_TYPES = (
        "string",
        "number",
        "boolean",
    )
    _js_properties_cache: dict[str, dict[str, type]] = {}
    _log_destructions: bool = DEBUGGING

    _object_id: str
    manager: JsObjectManager
    destroyed: bool
    _js_type: str = None
    
    @property
    def js_type(self):
        if self._js_type is None:
            # self.get_js_type()
            return "typeof not checked"
        return self._js_type
    
    @classmethod
    def set_js_properties_cache(cls, value: dict[str, type]):
        cls._js_properties_cache[cls] = value
    
    @classmethod
    def get_js_properties_cache(cls):
        if cls not in cls._js_properties_cache:
            return None
        
        return cls._js_properties_cache[cls]

    def __init__(
        self,
        base: JsObject = None,
        *,
        manager: JsObjectManager=None,
        fn_code: str = None,
        args: Union[dict, JsObject] = {},
        convert_args: bool = True,
        object_id: str = None,
    ):
        self.destroyed = False

        if base is not None:
            self._object_id = base._object_id
            # Unlinking:
            base._object_id = None
            self.manager = base.manager

        else:
            self._object_id = object_id 
            if self._object_id is None:
                self._object_id = str(uuid.uuid4())
            self.manager = manager

        if fn_code is not None:
            if convert_args:
                args = self.manager.from_py(args)

            call = JsObjectManagerCall(self, "fadd")
            self.manager.fadd_fn.Call(self._object_id, fn_code, args, call.on_complete)
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

    def __repr__(self):
        retVal = f"{type(self).__name__} {self._object_id}: <{self.js_type}> "
        if self.js_type in self.REPR_TYPES:
            retVal += str(self.py())
        else:
            retVal += "..."
        return retVal


    def __getattr__(self, name: str) -> Any:
        props = self._get_js_properties()
        if name in props.keys():
            retVal = self[name]
            
            # Convert to subclass when specified:
            if props[name] != JsObject:
                retVal = retVal.as_type(props[name])
            
            return retVal
        
        raise AttributeError(name)
    
    def __setattr__(self, name: str, value: Any) -> None:
        props = self._get_js_properties()
        if name in props.keys():
            self[name] = value
            return None
        
        return super().__setattr__(name, value)

    def _get_js_properties(self) -> dict[str, type[JsObject]]:
        cache = self.get_js_properties_cache()
        
        def type_check(elem):
            # print(elem)
            try:
                r = issubclass(elem[1], JsObject)
                # print (f"{r=}")
                return r
            except TypeError as e:
                # print(f"{elem[1]} is not a type.")
                return False
        
        if cache is None:
            cache = dict(filter(
                # lambda elem: issubclass(elem[1], JsObject),
                type_check,
                get_type_hints(type(self)).items()
            ))
        self.set_js_properties_cache(cache)
        
        return cache

    def check_destroyed_error(self, call: JsObjectManagerCall, raise_error: bool = True):
        if raise_error and self.destroyed:
            raise JsObjectManagerCallDestroyedException(call)
    
    # Regular Methods:
    def _wait_successful(self, call: JsObjectManagerCall):
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

    def destroy(self):
        self.destroyed = True
        # print(f"Destroying {self._object_id}...")
        self.manager.remove_fn.Call(
            self._object_id,
            lambda: (
                logger.debug(f"Destroyed JsObject {self._object_id}")
                if self._log_destructions
                else None
            ),
        )

    def access(
        self,
        fn_code: str,
        args: Union[dict, JsObject] = {},
        convert_args: bool = True,
        *,
        obj_param="self",
    ) -> JsObject:
        call = JsObjectManagerCall(self, "access")
        # Check to see which args are other JsObjects. If any are, we'll let
        # CEF know to replace those with their actual JavaScript counterparts.
        self.check_destroyed_error(call)
        
        if convert_args:
            args = self.manager.from_py(args)

        self.manager.access_fn.Call(
            self._object_id, fn_code, args, obj_param, call.on_complete
        )

        call.wait()

        if not self._wait_successful(call):
            return None

        return self.manager.from_id(call.result)

    def as_type(self, new_type: type[JsObject]):
        retVal = self.manager.from_id(self._object_id, new_type)
        
        # Unlinking own reference
        self._object_id = None
        
        return retVal
        
    def new(self, *args):
        return self.access("return new self(...args)", {"args": args})
        
    def py(self) -> Any:
        call = JsObjectManagerCall(self, "py")
        self.check_destroyed_error(call)
        
        self.manager.py_fn.Call(self._object_id, call.on_complete)

        call.wait()

        if not self._wait_successful(call):
            return None

        return call.result

    def get_js_type(self) -> Any:
        call = JsObjectManagerCall(self, "get_type")
        self.check_destroyed_error(call)
        
        self.manager.get_type_fn.Call(self._object_id, call.on_complete)

        call.wait()

        if not self._wait_successful(call):
            return None
        
        self._js_type = call.result
        return call.result

    def get_attr(self, name: str) -> JsObject:
        call = JsObjectManagerCall(self, "get_attr")
        self.check_destroyed_error(call)
        
        self.manager.get_attr_fn.Call(self._object_id, name, call.on_complete)

        call.wait()

        if not self._wait_successful(call):
            return None

        return self.manager.from_id(call.result)
        

    def set_attr(self, name: str, value: Any) -> JsObject:

        call = JsObjectManagerCall(self, "set_attr", timeout=None)
        self.check_destroyed_error(call)
        
        self.manager.set_attr_fn.Call(
            self._object_id, name, self.manager.from_py(value), call.on_complete
        )

        call.wait()

        if not self._wait_successful(call):
            return None

        return call.result

    def has_attr(self, name: str) -> JsObject:
        call = JsObjectManagerCall(self, "has_attr")
        self.check_destroyed_error(call)
        
        self.manager.has_attr_fn.Call(self._object_id, name, call.on_complete)

        call.wait()

        if not self._wait_successful(call):
            return None

        return call.result

    def del_attr(self, name: str) -> JsObject:
        call = JsObjectManagerCall(self, "del_attr")
        self.check_destroyed_error(call)
        
        self.manager.del_attr_fn.Call(self._object_id, name, call.on_complete)

        call.wait()

        if not self._wait_successful(call):
            return None

        return self.manager.from_id(call.result)

    def call(self, *args) -> JsObject:
        pass_args = self.manager.from_py(args)

        call = JsObjectManagerCall(self, "call")
        self.check_destroyed_error(call)
        
        self.manager.call_fn.Call(self._object_id, pass_args, call.on_complete)

        # del args_test

        call.wait()

        if not self._wait_successful(call):
            return None

        return self.manager.from_id(call.result)

    def call_method(self, method_name: str, *args) -> JsObject:
        pass_args = self.manager.from_py(args)

        call = JsObjectManagerCall(self, "call_method")
        self.check_destroyed_error(call)
        
        self.manager.call_method_fn.Call(
            self._object_id, method_name, pass_args, call.on_complete
        )

        call.wait()

        if not self._wait_successful(call):
            return None

        return self.manager.from_id(call.result)
