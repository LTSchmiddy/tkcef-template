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
        self.app_scope.set_var(
            "printr",
            lambda *args, **kwargs: print(" ".join([repr(i) for i in args]), **kwargs),
        )
        
    def load_element(self, template: str, *args, **kwargs):
        return self.document.htmlToElement(self.load_element_code(template, *args, **kwargs))
    
    def load_element_code(self, template: str, *args, **kwargs):
        return ui.loader.get_template(template).render(*args, **kwargs)
        
    def start(self):
        # self.window = self.js_object_manager.from_func("return window;")
        self.window = JsWindow(self.js_object_manager.from_func("return window;"))
        self.document = self.window.document

        self.root = self.document.get_element("#page-root")
        self.root.access("self.append(x)", {'x': self.load_element("root.html")})

    def update(self):
        pass
