import jinja2
import settings


loader = jinja2.Environment(
    loader=jinja2.PackageLoader(
        package_name="ui", package_path=str(settings.template_dir)
    ),
    autoescape=jinja2.select_autoescape(),
    extensions=["jinja2.ext.do", "jinja2.ext.loopcontrols"],
)
