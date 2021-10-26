from __future__ import annotations

from pathlib import Path
import traceback
import threading

from cefpython3 import cefpython as cef

from util import anon_func as af
from .js_preload import JsPreloadScript
from .browser_namespace import BrowserNamespaceWrapper
from .js_object import JsObjectManager, JsObject


class PyScopeManager:
    auto_convert_types: list[str] = ["boolean", "number", "string"]

    browser: cef.PyBrowser

    js_preload: JsPreloadScript
    js_object_manager: JsObjectManager

    def __init__(self, js_object_manager: JsObjectManager = None):
        self.js_object_manager = js_object_manager

        self.js_preload = JsPreloadScript.new_from_file_path(
            Path(__file__).parent.joinpath("js/pyscope_preload.js")
        )

    def config_in_browser(self, browser: cef.PyBrowser):
        self.js_preload.run(browser)

    def make_w_args(self, do_auto_convert: bool, args: list) -> list:
        retVal = []

        for i in args:
            new_obj = self.js_object_manager.from_id(i)

            if do_auto_convert and new_obj.js_type in self.auto_convert_types:
                retVal.append(new_obj.py())
            else:
                retVal.append(new_obj)

        return retVal

    def make_w_kwargs(self, do_auto_convert: bool, kwargs: dict) -> dict:
        retVal = {}

        for key, value in kwargs.items():
            new_obj = self.js_object_manager.from_id(value)

            if do_auto_convert and new_obj.js_type in self.auto_convert_types:
                retVal[key] = new_obj.py()
            else:
                retVal[key] = new_obj

        return retVal

    def create(
        self, call_id: str, complete_callback: cef.JavascriptCallback, kwargs: dict
    ):
        retVal = {"result": None, "error": None}
        try:

            if not kwargs["allow_new"]:
                # Making sure the namespace exists, and triggers an error if not:
                scope = BrowserNamespaceWrapper.namespaces[kwargs["id"]]
                retVal["result"] = {"name": scope.name, "is_new": False}

            elif "id" in kwargs and kwargs["id"] is not None:
                will_create = BrowserNamespaceWrapper.namespace_exists(kwargs["id"])

                retVal["result"] = {
                    "name": BrowserNamespaceWrapper.create_namespace_if_dne(
                        kwargs["id"]
                    ),
                    "is_new": will_create,
                }
            else:
                retVal["result"] = {
                    "name": BrowserNamespaceWrapper.create_new_namespace(),
                    "is_new": True,
                }

        except Exception as e:
            retVal["error"] = {
                "message": str(e),
                "name": type(e).__name__,
                "stack": traceback.format_exc(),
            }

        complete_callback.Call(call_id, retVal)

    def destroy(
        self, call_id: str, complete_callback: cef.JavascriptCallback, kwargs: dict
    ):
        retVal = {"result": None, "error": None}
        try:

            retVal["result"] = BrowserNamespaceWrapper.remove_namespace(kwargs["id"])

        except Exception as e:
            retVal["error"] = {
                "message": str(e),
                "name": type(e).__name__,
                "stack": traceback.format_exc(),
            }

        complete_callback.Call(call_id, retVal)

    def exec(
        self, call_id: str, complete_callback: cef.JavascriptCallback, kwargs: dict
    ):
        retVal = {"result": None, "error": None}
        try:
            ns = BrowserNamespaceWrapper.namespaces[kwargs["id"]]
            retVal["result"] = ns.exec(
                kwargs["code"],
                kwargs["ret_name"],
                kwargs["params"],
            )
        except Exception as e:
            retVal["error"] = {
                "message": str(e),
                "name": type(e).__name__,
                "stack": traceback.format_exc(),
            }

        complete_callback.Call(call_id, retVal)

    def w_exec_runner(self, *args, **kwargs):
        thread = threading.Thread(None, self.w_exec, args=args, kwargs=kwargs)
        thread.start()

    def w_exec(
        self, call_id: str, complete_callback: cef.JavascriptCallback, kwargs: dict
    ):
        retVal = {"result": None, "error": None}
        try:
            ns = BrowserNamespaceWrapper.namespaces[kwargs["id"]]
            retVal["result"] = ns.exec(
                kwargs["code"],
                kwargs["ret_name"],
                self.make_w_kwargs(kwargs["do_auto_convert"], kwargs["params"]),
            )
        except Exception as e:
            retVal["error"] = {
                "message": str(e),
                "name": type(e).__name__,
                "stack": traceback.format_exc(),
            }

        complete_callback.Call(call_id, retVal)

    def do_func(
        self, call_id: str, complete_callback: cef.JavascriptCallback, kwargs: dict
    ):
        retVal = {"result": None, "error": None}
        try:
            ns = BrowserNamespaceWrapper.namespaces[kwargs["id"]]
            retVal["result"] = ns.do_func(
                kwargs["code"],
                kwargs["params"],
            )
        except Exception as e:
            retVal["error"] = {
                "message": str(e),
                "name": type(e).__name__,
                "stack": traceback.format_exc(),
            }

        complete_callback.Call(call_id, retVal)

    def w_do_func_runner(self, *args, **kwargs):
        thread = threading.Thread(None, self.w_do_func, args=args, kwargs=kwargs)
        thread.start()

    def w_do_func(
        self, call_id: str, complete_callback: cef.JavascriptCallback, kwargs: dict
    ):
        retVal = {"result": None, "error": None}
        try:
            ns = BrowserNamespaceWrapper.namespaces[kwargs["id"]]
            retVal["result"] = ns.do_func(
                kwargs["code"],
                self.make_w_kwargs(kwargs["do_auto_convert"], kwargs["params"]),
            )
        except Exception as e:
            retVal["error"] = {
                "message": str(e),
                "name": type(e).__name__,
                "stack": traceback.format_exc(),
            }

        complete_callback.Call(call_id, retVal)

    def make_func(
        self, call_id: str, complete_callback: cef.JavascriptCallback, kwargs: dict
    ):
        retVal = {"result": None, "error": None}
        try:
            ns = BrowserNamespaceWrapper.namespaces[kwargs["id"]]
            retVal["result"] = ns.make_func(
                kwargs["name"],
                kwargs["code"],
                kwargs["params"],
            )
        except Exception as e:
            retVal["error"] = {
                "message": str(e),
                "name": type(e).__name__,
                "stack": traceback.format_exc(),
            }

        complete_callback.Call(call_id, retVal)

    def get_var(
        self, call_id: str, complete_callback: cef.JavascriptCallback, kwargs: dict
    ):
        retVal = {"result": None, "error": None}
        try:
            ns = BrowserNamespaceWrapper.namespaces[kwargs["id"]]
            retVal["result"] = ns.get_var(
                kwargs["name"],
            )
        except Exception as e:
            retVal["error"] = {
                "message": str(e),
                "name": type(e).__name__,
                "stack": traceback.format_exc(),
            }

        complete_callback.Call(call_id, retVal)

    def has_var(
        self, call_id: str, complete_callback: cef.JavascriptCallback, kwargs: dict
    ):
        retVal = {"result": None, "error": None}
        try:
            ns = BrowserNamespaceWrapper.namespaces[kwargs["id"]]
            retVal["result"] = ns.has_var(
                kwargs["name"],
            )
        except Exception as e:
            retVal["error"] = {
                "message": str(e),
                "name": type(e).__name__,
                "stack": traceback.format_exc(),
            }

        complete_callback.Call(call_id, retVal)

    def del_var(
        self, call_id: str, complete_callback: cef.JavascriptCallback, kwargs: dict
    ):
        retVal = {"result": None, "error": None}
        try:
            ns = BrowserNamespaceWrapper.namespaces[kwargs["id"]]
            retVal["result"] = ns.del_var(
                kwargs["name"],
                kwargs["value"],
            )
        except Exception as e:
            retVal["error"] = {
                "message": str(e),
                "name": type(e).__name__,
                "stack": traceback.format_exc(),
            }

        complete_callback.Call(call_id, retVal)

    def set_var(
        self, call_id: str, complete_callback: cef.JavascriptCallback, kwargs: dict
    ):
        retVal = {"result": None, "error": None}
        try:
            ns = BrowserNamespaceWrapper.namespaces[kwargs["id"]]
            retVal["result"] = ns.set_var(
                kwargs["name"],
                kwargs["value"],
            )
        except Exception as e:
            retVal["error"] = {
                "message": str(e),
                "name": type(e).__name__,
                "stack": traceback.format_exc(),
            }

        complete_callback.Call(call_id, retVal)

    def raw_call_runner(self, *args, **kwargs):
        thread = threading.Thread(None, self.raw_call, args=args, kwargs=kwargs)
        thread.start()

    def raw_call(
        self, call_id: str, complete_callback: cef.JavascriptCallback, params: dict
    ):
        retVal = {"result": None, "error": None}
        try:
            ns = BrowserNamespaceWrapper.namespaces[params["id"]]
            retVal["result"] = ns.call(
                params["name"],
                params["args"],
                params["kwargs"],
            )
        except Exception as e:
            retVal["error"] = {
                "message": str(e),
                "name": type(e).__name__,
                "stack": traceback.format_exc(),
            }

        complete_callback.Call(call_id, retVal)

    def w_call_runner(self, *args, **kwargs):
        thread = threading.Thread(None, self.w_call, args=args, kwargs=kwargs)
        thread.start()

    def w_call(
        self, call_id: str, complete_callback: cef.JavascriptCallback, params: dict
    ):
        retVal = {"result": None, "error": None}
        try:
            args = self.make_w_args(params["auto_convert"], params["args"])
            kwargs = self.make_w_kwargs(params["auto_convert"], params["kwargs"])

            ns = BrowserNamespaceWrapper.namespaces[params["id"]]
            retVal["result"] = ns.call(
                params["name"],
                args,
                kwargs,
            )
        except Exception as e:
            retVal["error"] = {
                "message": str(e),
                "name": type(e).__name__,
                "stack": traceback.format_exc(),
            }

        complete_callback.Call(call_id, retVal)
