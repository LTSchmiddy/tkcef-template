from cefpython3 import cefpython as cef

import ui


class TemplateBindings:
    def get_page_root(self, callback: cef.JavascriptCallback):
        main_template = ui.loader.get_template("root.html")
        callback.Call(main_template.render())
