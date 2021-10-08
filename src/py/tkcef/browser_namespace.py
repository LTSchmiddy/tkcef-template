from __future__ import annotations

from types import ModuleType
import random 
from typing import Union

from cefpython3 import cefpython as cef

from util import anon_func as af


class BrowserNamespaceWrapper:
    _mod: ModuleType
    _mod_locals: dict
    global_level: bool

    _name: str
    _doc: str

    def __init__(self, name, doc: Union(str, None) = None, global_level=True, *, use_external: ModuleType = None):
        self._name = name
        
        if use_external is not None:
            self._mod = use_external

        else:
            if doc is None:
                doc = "A unique namespace for running In-Browser Python code."

            self._mod = ModuleType("name", f"(BrowserNamespace: {self._name}) " + doc)
            
            
        self._mod_locals = {}
        # Lets be honest, I don't there'd ever be much reason for this to be false.
        self.global_level = global_level


    def reset(self):
        self._mod = ModuleType("name", f"(BrowserNamespace: {self._name}) " + self.doc)
        self._mod_locals = {}


    @property
    def name(self):
        return self._mod.__name__

    @property
    def doc(self):
        return self._mod.__doc__

    @property
    def globals(self):
        return self._mod.__dict__

    @globals.setter
    def globals(self, value):
        self._mod.__dict__ = value

    @property
    def locals(self):
        if self.global_level:
            return self.globals
        return self._mod_locals

    @locals.setter
    def locals(self, value):
        if self.global_level:
            self.globals = value
        self._mod_locals = value

    def get_var(self, attr):
        return getattr(self._mod, attr)

    def set_var(self, attr, val):
        setattr(self._mod, attr, val)

    def has_var(self, attr):
        return hasattr(self._mod, attr)

    def del_var(self, attr):
        return delattr(self._mod, attr)

    def call(self, attr, args=(), kwargs=None, no_return=False):
        if kwargs is None:
            kwargs = {}

        if no_return:
            getattr(self._mod, attr)(*args, **kwargs)
            return None
        else:
            return getattr(self._mod, attr)(*args, **kwargs)

    def exec(self, p_code, p_return=None, params: Union(dict, None) = None):

        if isinstance(params, dict):
            # This should allow us to pass JS variables into the python code, without cluttering up the global namespace.

            self.locals.update(params)
            retVal = af.rexec(
                p_code,
                p_return,
                self.globals,
                self.locals,
                f"{__name__}.{self.name}",
            )
            return retVal

        else:
            return af.rexec(
                p_code,
                p_return,
                self.globals,
                self.locals,
                f"{__name__}.{self.name}",
            )

    def do_func(self, code: str, args: dict=None, main_globals=True):
        if args is None:
            args = {}

        if main_globals:
            return af.func(
                tuple(args.keys()),
                code,
                __globals=self.globals,
                __locals=self.locals,
                collect_locals=False,
            )(*tuple(args.values()))
        else:
            return af.func(tuple(args.keys()), code, collect_locals=False)(
                *tuple(args.values())
            )

    def make_func(self, name: str, code: str, args: list=None, main_globals=True):
        if args is None:
            args = {}

        fn = None
        if main_globals:
            fn = af.func(
                args,
                code,
                name=name,
                __globals=self.globals,
                __locals=self.locals,
                collect_locals=False,
            )
        else:
            fn = af.func(args, code, name=name, collect_locals=False)
        
        if name is not None:
            self.set_var(name, fn)
        return fn

    # Static Info:
    max_namespaces = 100000
    namespaces: dict[str, BrowserNamespaceWrapper] = {}
    
    @classmethod
    def get_new_namespace_id(cls):
        new_id = "n-py0"
        print(new_id)
        while new_id in cls.namespaces:
            new_id = f"n-py{random.randint(1, cls.max_namespaces)}"
            print(new_id)
            
        return new_id

    @classmethod
    def create_new_namespace(cls, name: str = "", global_level=True, *, use_external: ModuleType = None):
        if name == "" or name is None:
            name = cls.get_new_namespace_id()

        cls.namespaces[name] = BrowserNamespaceWrapper(
            name,
            f"A unique namespace for running In-Browser Python code. Namespace: {name}",
            global_level,
            use_external=use_external
        )
        return name

    @classmethod
    def create_namespace_if_dne(cls, name: str, global_level=True, *, use_external: ModuleType = None):
        if name in cls.namespaces:
            return name

        cls.namespaces[name] = BrowserNamespaceWrapper(
            name,
            f"A unique namespace for running In-Browser Python code. Namespace: {name}",
            global_level,
            use_external=use_external
        )
        return name

    @classmethod
    def remove_namespace(cls, name: str):
        del cls.namespaces[name]

    @classmethod
    def namespace_exists(cls, name: str = ""):
        return name in cls.namespaces

    @classmethod
    def global_reset(cls):
        cls.namespaces = {}
        # cls.namespaces = {
        #     "main": BrowserNamespaceWrapper(
        #         "main", "Primary namespace for running In-Browser Python code", False
        #     )
        # }
        
        # if add_main:
        #     self.globals.update({"main": self.namespaces["main"]})
        
BrowserNamespaceWrapper.global_reset()