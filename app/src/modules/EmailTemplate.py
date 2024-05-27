from modules.Transformer import Activity, Summary
from jinja2 import Environment, FileSystemLoader, select_autoescape
from dataclasses import dataclass, field
import css_inline


@dataclass
class EmailSummary:
    date: str = ''
    activities: list[Activity] = field(default_factory=list)
    summary: Summary = field(default_factory=Summary)


class EmailTemplate:

    def __init__(self, template_root: str, template_name='email.html'):
        """ Setup template."""

        env = Environment(loader=FileSystemLoader(template_root),
                          autoescape=select_autoescape(['html', 'xml']))
        self.template = env.get_template(template_name)

    def generateHTML(self, data: EmailSummary) -> str:
        """ Use email template to generate html from data."""

        html = self.template.render(data=data)
        return css_inline.inline(html, keep_style_tags=True)
