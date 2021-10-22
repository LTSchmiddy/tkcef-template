from __future__ import annotations, generator_stop
from types import ModuleType
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
from types import ModuleType

import threading
import tkinter as tk
import sys
import time
import platform
import logging as _logging
import sched
import uuid

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


def with_uuid4(callback: cef.JavascriptCallback):
    id = uuid.uuid4()
    callback.Call(str(id))


class AppManager:
    root_frames: dict[str, WebFrame]
    keys_to_add: dict[str, WebFrame]
    keys_to_remove: list[str]

    thread: threading.Thread
    update_interval: Union[int, float]
    update_sched: sched.scheduler

    next_update_event: sched.Event

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

        self.next_update_event = None

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
        sys.excepthook = cef.ExceptHook
        # To shutdown all CEF processes on error
        # Tk must be initialized before CEF otherwise fatal error (Issue #306)
        cef_config = {}
        if MAC:
            cef_config["external_message_pump"] = True
        else:
            # Using the multi_threaded_message_loop.
            # Helps prevent various GIL-related crashes:
            cef_config["multi_threaded_message_loop"] = True

        cef.Initialize(settings=cef_config, switches={"allow-file-access": ""})

        self.root_frames = {}
        self.keys_to_add = {}
        self.keys_to_remove = []

    def add_webapp(
        self,
        key: str,
        app: webapp.WebApp,
        title: str = "TkCef App",
        show_navbar: bool = False,
        geometry: str = "900x640",
        menubar_builder: Callable[[tk.Tk], tk.Menu] = None,
    ):

        root = tk.Tk()

        menubar = None
        if menubar_builder is not None:
            menubar = menubar_builder(root)

        else:
            menubar = app.construct_menubar(root)

        # frame = WebFrame(
        frame = app.tk_frame_class(
            root,
            app,
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
            # Using sched to control the timing of the mainloop is
            # a lot more consistent than using time.sleep() directly.
            self.next_update_event = self.update_sched.enter(
                self.update_interval,
                0,
                lambda: None,
                # A bit of an odd choice, sure. But way, we don't have to run
                # the update before scheduling the next one.
            )
            self.mainloop_step()
            self.update_sched.run()

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
            frame.app._run_step()

            # else:
            # print(f"INFO: AppManager update attempted from incorrect thread: {threading.currentThread().name}")

        # If any windows were closed, remove them from roots:
        if len(self.keys_to_remove) > 0:
            for i in self.keys_to_remove:
                if i in self.root_frames:
                    del self.root_frames[i]
            self.keys_to_remove.clear()

    def shutdown(self):
        logger.debug("CEF is shutting down now...")
        cef.Shutdown()

    def __del__(self):
        logger.debug("ALERT: AppManager is being garbage collected.")
        self.shutdown()


from .webapp import WebApp
from .js_object import JsObject
from .frame import WebFrame
from .browser_namespace import BrowserNamespaceWrapper


def expose_namespace(module: ModuleType, name: str = None) -> str:
    return BrowserNamespaceWrapper.create_namespace_if_dne(
        module.__name__ if name is None else name, use_external=module
    )
