import tkcef, settings, jsbind

from tkcef import WebApp, JsObject

class TestApp(tkcef.WebApp):
    window: JsObject
    
    def __init__(self):
        super().__init__()
        
        self.document_path = settings.webpack_dir.joinpath("index.html").absolute().as_uri()
        self.js_bind_objects = jsbind.bindings
    
    def start(self):
        self.window = self.js_object_manager.from_func("return window;")
        print(repr(self.window))
    
    def update(self):
        pass