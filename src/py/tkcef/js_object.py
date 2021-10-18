from __future__ import annotations

from pathlib import Path
import traceback

from cefpython3 import cefpython as cef

from .js_preload import JsPreloadScript
from util import anon_func as af


class JsObjectManager:
    browser: cef.PyBrowser

    js_preload: JsPreloadScript

    def __init__(self):
        self.js_preload = JsPreloadScript.new_from_file_path(
            Path(__file__).parent.joinpath("js/jsobject_preload.js")
        )

    def config_in_browser(self, browser: cef.PyBrowser):
        self.js_preload.run(browser)
