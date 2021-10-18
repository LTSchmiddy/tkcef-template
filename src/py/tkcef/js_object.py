from __future__ import annotations

from pathlib import Path
import traceback
from typing import Any
import uuid
import threading

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

    def get_object(self, fn_code):
        return JsObject(self, fn_code)

    def ready(self):
        self.is_ready = True


class JsObject:
    object_id: str
    return_items: dict[str, Any]
    manager: JsObjectManager

    def __init__(self, manager: JsObjectManager, fn_code: str):
        self.object_id = uuid.uuid4()
        self.return_items = {}

        self.manager = manager

        self.manager.fadd_fn.Call(self.object_id, fn_code, lambda: print("Created..."))

    def __del__(self):
        self.manager.remove_fn.Call(self.object_id, lambda: print("Destroyed..."))
