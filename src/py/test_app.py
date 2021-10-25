import tkcef, settings, jsbind

from tkcef import WebApp, JsObject
from tkcef.js_types import JsWindow


class TestApp(tkcef.WebApp):
    window: JsWindow

    def __init__(self):
        super().__init__()

        self.document_path = (
            settings.webpack_dir.joinpath("index.html").absolute().as_uri()
        )
        self.js_bind_objects = jsbind.bindings
    
    def js_config(self):
        super().js_config()
    
        self.app_scope.set_var("print", print)
        self.app_scope.set_var("printr", lambda *args, **kwargs: print(" ".join([repr(i) for i in args]), **kwargs))


    def start(self):
        self.window = JsWindow(self.js_object_manager.from_func("return window;"))
        print(repr(self.window))
        print(repr(self.window.document))
        print(repr(self.window.document.head))
    
        
        # print(f"{self.window._get_js_properties()=}")
    
    def update(self):
        pass
