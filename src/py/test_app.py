import tkcef, settings
from tkcef import WebApp, JsObject
from tkcef.js_types import JsWindow

import ui

class TestApp(tkcef.WebApp):
    window: JsWindow

    def __init__(self):
        super().__init__()

        self.document_path = (
            settings.webpack_dir.joinpath("index.html").absolute().as_uri()
        )
    
    def js_config(self):
        super().js_config()
    
        self.app_scope.set_var("print", print)
        self.app_scope.set_var("printr", lambda *args, **kwargs: print(" ".join([repr(i) for i in args]), **kwargs))


    def start(self):
        pass
        # self.window = JsWindow(self.js_object_manager.from_func("return window;"))
        # # self.window.access("console.log(self)")
        # self.document = self.window.document
        
        # print(repr(self.window))
        
        # print("===== Access Test Start =====")
        
        # self.document.access("console.log(x)", {'x': [33, 55, {"y": self.window, "hi": "alex"}]})
        # print("===== Access Test Complete =====")
        # # self.root = self.document.get_element("#page-root")
        
        # # self.root.access("self.append(x)", {'x': self.document.htmlToElement(ui.loader.get_template("root.html").render())})
        
        # print(self.document.title.py())
        # print(f"{self.window.innerHeight.py()=}")
    
    def update(self):
        pass
