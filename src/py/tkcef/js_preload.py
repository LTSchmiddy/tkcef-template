from __future__ import annotations
from pathlib import Path

from cefpython3 import cefpython as cef


class JsPreloadScript:
    path: Path = None
    code: str = None

    def __init__(self):
        pass

    def load_code_from_path(self):
        self.code = self.path.read_text()

    def run(self, browser: cef.PyBrowser):
        browser.ExecuteJavascript(self.code, self.path.as_uri(), 0)

    @classmethod
    def new_from_file_path(cls, fpath: Path) -> JsPreloadScript:
        retVal: JsPreloadScript = cls()
        retVal.path = fpath
        retVal.load_code_from_path()

        return retVal
