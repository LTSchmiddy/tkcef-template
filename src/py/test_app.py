import tkcef, settings, jsbind

from tkcef import WebApp, JsObject


class TestApp(tkcef.WebApp):
    window: JsObject

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
        self.window = self.js_object_manager.from_func("return window;")
        print(repr(self.window))       
        
        print(f"{self.window._get_js_properties()=}")
    
    def update(self):
        pass


class VlcApp(tkcef.App)