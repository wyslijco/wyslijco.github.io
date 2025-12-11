import os

from jinja2 import FileSystemLoader, Environment

from consts import OrgFormSchemaIds
from parsers import GithubIssueFormDataParser


def render_organization_yaml(data: GithubIssueFormDataParser):
    template_dir = os.path.dirname(os.path.abspath(__file__))
    env = Environment(loader=FileSystemLoader(template_dir), keep_trailing_newline=True)

    template = env.get_template("organization.yaml.j2")

    org_data = {field.name: data.get(field.value) for field in OrgFormSchemaIds}

    return template.render(organization=org_data)
