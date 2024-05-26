from jinja2 import Environment, FileSystemLoader, select_autoescape
from dataclasses import dataclass
import css_inline
from .Transformer import Activity, Summary


@dataclass
class EmailSummary:
    date: str
    activities: list[Activity]
    summary: Summary


class EmailTemplate:

    def __init__(self, template_root: str, template_name='email.html'):
        """ Setup template."""

        env = Environment(loader=FileSystemLoader(f'{template_root}/templates/'),
                          autoescape=select_autoescape(['html', 'xml']))
        self.template = env.get_template(template_name)

    def generateHTML(self, data: EmailSummary) -> str:
        """ Use email template to generate html from data."""

        html = self.template.render(data=data)
        return css_inline.inline(html, keep_style_tags=True)
