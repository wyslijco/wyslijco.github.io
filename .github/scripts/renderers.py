import os

from jinja2 import FileSystemLoader, Environment

from consts import OrgFormSchemaIds
from parsers import GithubIssueFormDataParser


def render_organization_yaml(data: GithubIssueFormDataParser):
    template_dir = os.path.dirname(os.path.abspath(__file__))
    env = Environment(loader=FileSystemLoader(template_dir))

    template = env.get_template("organization.yaml.j2")

    org_data = {field: data.get(field) for field in OrgFormSchemaIds.__members__.keys()}

    return template.render(organization=org_data)
