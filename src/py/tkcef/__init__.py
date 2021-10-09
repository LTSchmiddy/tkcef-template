from __future__ import annotations, generator_stop
from typing import Callable, Union

# Example of embedding CEF Python browser using Tkinter toolkit.
# This example has two widgets: a navigation bar and a browser.
#
# NOTE: This example often crashes on Mac (Python 2.7, Tk 8.5/8.6)
#       during initial app loading with such message:
#       "Segmentation fault: 11". Reported as Issue #309.
#
# Tested configurations:
# - Tk 8.5 on Windows/Mac
# - Tk 8.6 on Linux
# - CEF Python v55.3+
#
# Known issue on Linux: When typing url, mouse must be over url
# entry widget otherwise keyboard focus is lost (Issue #255
# and Issue #284).
# Other focus issues discussed in Issue #535.

import threading
import tkinter as tk
import sys
import time
import platform
import logging as _logging
import sched

from cefpython3 import cefpython as cef

MAIN_THREAD_NAME = "MainThread"

# Fix for PyCharm hints warnings
WindowUtils = cef.WindowUtils()

# Platforms
WINDOWS = platform.system() == "Windows"
LINUX = platform.system() == "Linux"
MAC = platform.system() == "Darwin"

# Globals
logger = _logging.getLogger("tkcef")

# Constants
# Tk 8.5 doesn't support png images
IMAGE_EXT = ".png" if tk.TkVersion > 8.5 else ".gif"

UPDATE_DELAY = 0.05


class AppManager:
    root_frames: dict[str, WebFrame]
    keys_to_add: dict[str, WebFrame]
    keys_to_remove: list[str]

    thread: threading.Thread
    update_interval: Union[int, float]
    update_sched: sched.scheduler

    @property
    def should_run(self) -> bool:
        return len(self.root_frames) > 0 or len(self.keys_to_add) > 0

    def __init__(
        self,
        *,
        update_interval: Union[int, float] = 0.05,
        update_sched: sched.scheduler = sched.scheduler(),
        cef_config: dict = {},
        thread: threading.Thread = threading.current_thread()
    ):
        self.thread = thread
        self.update_sched = update_sched
        self.update_interval = update_interval

        logger.setLevel(_logging.DEBUG)
        stream_handler = _logging.StreamHandler()
        formatter = _logging.Formatter("[%(filename)s] %(message)s")
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
        logger.info(
            "Python {ver} {arch}".format(
                ver=platform.python_version(), arch=platform.architecture()[0]
            )
        )
        logger.info("Tk {ver}".format(ver=tk.Tcl().eval("info patchlevel")))
        logger.info("CEF Python {ver}".format(ver=cef.__version__))
        assert cef.__version__ >= "55.3", "CEF Python v55.3+ required to run this"
        sys.excepthook = cef.ExceptHook  # To shutdown all CEF processes on error
        # Tk must be initialized before CEF otherwise fatal error (Issue #306)
        # Using the multi_threaded_message_loop,
        cef_config = {}
        if MAC:
            cef_config["external_message_pump"] = True
        else:
            # Helps prevent various GIL-related crashes:
            cef_config["multi_threaded_message_loop"] = True

        cef.Initialize(settings=cef_config, switches={"allow-file-access": ""})

        self.root_frames = {}
        self.keys_to_add = {}
        self.keys_to_remove = []

    def add_webapp(
        self,
        key: str,
        webview: webapp.WebApp,
        title: str = "Tkinter example",
        show_navbar: bool = False,
        geometry: str = "900x640",
        menubar_builder: Callable[[tk.Tk], tk.Menu] = None,
    ):

        root = tk.Tk()

        menubar = None
        if menubar_builder is not None:
            menubar = menubar_builder(root)

        frame = WebFrame(
            root,
            webview,
            title=title,
            show_navbar=show_navbar,
            geometry=geometry,
            menubar=menubar,
            app_manager=self,
            app_manager_key=key,
        )

        # self.keys_to_add[key] = root
        self.keys_to_add[key] = frame

    def remove_webapp(self, key: str):
        self.keys_to_remove.append(key)

    def wait_interval(self):
        time.sleep(self.update_interval)

    def mainloop(self):
        while self.should_run:
            self.mainloop_step()

    def mainloop_step(self):
        # Since we can't manipulate the roots dict while iterating through it,
        # we'll track whether or not windows should be added or removed, then handle them here.

        # If any windows were opened, add them to roots:
        if len(self.keys_to_add) > 0:
            self.root_frames.update(self.keys_to_add)
            self.keys_to_add.clear()

        # Update windows:
        for key, frame in self.root_frames.items():

            # if (threading.currentThread() == self.thread):
            frame.update_idletasks()
            frame.update()
            # else:
            # print(f"INFO: AppManager update attempted from incorrect thread: {threading.currentThread().name}")

        # If any windows were closed, remove them from roots:
        if len(self.keys_to_remove) > 0:
            for i in self.keys_to_remove:
                if i in self.root_frames:
                    del self.root_frames[i]
            self.keys_to_remove.clear()

    def shutdown(self):
        logger.debug("Main loop exited")
        cef.Shutdown()


from . import webapp
from .frame import WebFrame
from .browser_namespace import BrowserNamespaceWrapper
