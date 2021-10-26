from __future__ import annotations, generator_stop
import queue
from types import ModuleType
from typing import Any, Callable, Union

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
import os
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


class UpdateAction(Callable):
    # This class holds the definition for a function/method call
    # so it can triggered later. Used for queueing calls that must
    # performed on Tk's main/update thread.
    fn: Callable
    args: tuple[Any]
    kwargs: dict[str, Any]

    def __init__(self, fn: Union(Callable, cef.JavascriptCallback), *args, **kwargs):
        if isinstance(fn, cef.JavascriptCallback):
            self.fn = fn.Call
        else:
            self.fn = fn
        self.args = args
        self.kwargs = kwargs

    def call(self) -> Any:
        return self.fn(*self.args, **self.kwargs)

    def __call__(self) -> Any:
        return self.call()


class AppFrame(tk.Frame):
    @property
    def app_manager_key(self) -> str:
        return self.app.app_manager_key

    @property
    def app_manager(self) -> str:
        return self.app.app_manager

    def __init__(
        self, root, app, title: str = "Tkinter example", geometry: str = "900x640"
    ):

        self.updated_title: str = None

        # Setting relationships between root, frame, and webapp:
        # self.root.webframe = self
        self.app: App = app

        # Root
        root.geometry(geometry)

        # MainFrame
        tk.Frame.__init__(self, root)

        # Add Menubar:
        menubar = self.app.construct_menubar(root)
        if menubar is not None:
            self.set_menubar(menubar)

        self.master.title(title)
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)
        self.master.bind("<Configure>", self.on_root_configure)
        self.setup_icon()
        self.bind("<Configure>", self.on_configure)
        self.bind("<FocusIn>", self.on_focus_in)
        self.bind("<FocusOut>", self.on_focus_out)

        tk.Grid.rowconfigure(self, 0, weight=0)
        tk.Grid.columnconfigure(self, 0, weight=0)

        # Pack MainFrame
        self.pack(fill=tk.BOTH, expand=tk.YES)

    def set_menubar(self, menubar: tk.Menu):
        self.menubar = menubar
        self.master.config(menu=self.menubar)

    def on_root_configure(self, _):
        logger.debug(f"{type(self).__name__}.on_root_configure")

    def on_configure(self, event):
        logger.debug(f"{type(self).__name__}.on_configure")

    def on_focus_in(self, _):
        logger.debug(f"{type(self).__name__}.on_focus_in")

    def on_focus_out(self, _):
        logger.debug(f"{type(self).__name__}.on_focus_out")

    def on_close(self):
        self.app.close()

    def destroy(self):
        self.master = None
        self.app = None

    def setup_icon(self):
        resources = os.path.join(os.path.dirname(__file__), "resources")
        icon_path = os.path.join(resources, "tkinter" + IMAGE_EXT)
        if os.path.exists(icon_path):
            self.icon = tk.PhotoImage(file=icon_path)
            # noinspection PyProtectedMember
            self.master.call("wm", "iconphoto", self.master._w, self.icon)

    def update(self):
        super().update()


class App:
    app_manager: AppManager = None
    app_manager_key: str = None

    tk_root: tk.Tk
    tk_frame: tk.Frame
    tk_frame_class: type[tk.Frame]
    _on_update_queue: queue.Queue[UpdateAction]

    def __init__(
        self,
        *,
        tk_frame_class: type[tk.Frame] = AppFrame,
    ):
        self.tk_frame: tk.Frame = None
        self.tk_frame_class = tk_frame_class
        self._on_update_queue = queue.Queue()

    def setup(self, key: str, app_manager: AppManager, construct_frame: bool = True):
        self.app_manager: AppManager = app_manager
        self.app_manager_key: str = key

        if construct_frame:
            self.tk_root = tk.Tk()
            self.tk_frame = self.tk_frame_class(self.tk_root, self)

    def _run_step(self):
        self.tk_frame.update_idletasks()
        self.tk_frame.update()

        # Handle queued actions:
        while not self._on_update_queue.empty():
            self._on_update_queue.get().call()

        # Update as normal:
        self.update()

    def update(self):
        pass

    def destroy(self):
        self.tk_root.destroy()
        self.tk_frame = None
        self.tk_root = None

        # All references must be cleared for CEF to shutdown cleanly.

    def close(self):
        if self.app_manager is not None and self.app_manager_key is not None:
            self.app_manager.remove(self.app_manager_key)

    def queue_update_action(
        self, fn: Union(Callable, cef.JavascriptCallback), *args, **kwargs
    ):
        self._on_update_queue.put(UpdateAction(fn, *args, **kwargs))

    def set_geometry(self, width: int, height: int):
        self.queue_update_action(self.tk_frame.root.geometry, f"{width}x{height}")

    # In most cases, these 4 methods are the main ones you want to override:
    def construct_menubar(self, root: tk.Tk) -> tk.Menu:
        menubar = tk.Menu(root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.close)
        menubar.add_cascade(label="File", menu=filemenu)

        return menubar


class AppManager:
    apps: dict[str, App]
    keys_to_add: dict[str, App]
    keys_to_remove: list[str]

    using_cef: bool
    thread: threading.Thread
    update_interval: Union[int, float]
    update_sched: sched.scheduler

    next_update_event: sched.Event

    @property
    def should_run(self) -> bool:
        return len(self.apps) > 0 or len(self.keys_to_add) > 0

    def __init__(
        self,
        *,
        update_interval: Union[int, float] = 0.05,
        update_sched: sched.scheduler = sched.scheduler(),
        cef_config: dict = {},
        thread: threading.Thread = threading.current_thread(),
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

        self.apps = {}
        self.keys_to_add = {}
        self.keys_to_remove = []

    def add(self, app: webapp.WebApp, key: str = None):
        if key is None:
            key = "APP_" + str(uuid.uuid4()).replace("-", "_")
        
        self.keys_to_add[key] = app

    def remove(self, key: Union[str, App]):
        if isinstance(key, App):
            key = key.app_manager_key
        
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
            for key, value in self.keys_to_add.items():
                value.setup(key, self)
                
            self.apps.update(self.keys_to_add)
            self.keys_to_add.clear()

        # Update windows:
        for key, app in self.apps.items():
            # if (threading.currentThread() == self.thread):
            app._run_step()

        # If any windows were closed, remove them from roots:
        if len(self.keys_to_remove) > 0:
            for i in self.keys_to_remove:
                if i in self.apps:
                    self.apps[i].destroy()
                    del self.apps[i]
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
