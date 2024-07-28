import os
from jinja2 import Environment, FileSystemLoader, select_autoescape

# Nastavenie Jinja2 prostredia
env = Environment(
    loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")),
    autoescape=select_autoescape(['html', 'xml'])
)

def render_template(template_name, **kwargs):
    template = env.get_template(template_name)
    return template.render(kwargs)
