from modules.Transformer import EmailTemplateData
from jinja2 import Environment, FileSystemLoader, select_autoescape
import css_inline


class EmailTemplate:

    def __init__(self, template_root: str, asset_url: str, template_name='email.html'):
        """ Setup template."""

        env = Environment(loader=FileSystemLoader(template_root),
                          autoescape=select_autoescape(['html', 'xml']))
        self.template = env.get_template(template_name)
        self.asset_url = asset_url

    def generateHTML(self, data: EmailTemplateData) -> str:
        """ Use email template to generate html from data."""

        html = self.template.render(data=data, asset_url=self.asset_url)
        return css_inline.inline(html, keep_style_tags=True)
