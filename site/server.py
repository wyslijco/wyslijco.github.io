import os
import sys

import yaml
from flask import Flask, render_template
from flask_frozen import Freezer  # Added

from config import ORGANIZATIONS_DIR_PATH, ORGANIZATIONS_SLUG_FIELD_NAME

DEBUG = True
FREEZER_DESTINATION = "../_site"  # builds to the default desitination for GitHub Pages

app = Flask(__name__)
app.config.from_object(__name__)
freezer = Freezer(app)


def get_organizations() -> dict[str, str]:
    organization_files = filter(lambda x: x.endswith(".yaml"), os.listdir(ORGANIZATIONS_DIR_PATH))
    organizations = dict()
    for organization_file in organization_files:
        with open(f"{ORGANIZATIONS_DIR_PATH}/{organization_file}") as org:
            organization = yaml.safe_load(org)
            organizations[organization.get(ORGANIZATIONS_SLUG_FIELD_NAME)] = organization_file
    return organizations


organizations: dict[str, str] = get_organizations()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/<string:org_name>/")
def organization_page(org_name):
    filename = organizations.get(org_name)
    with open(f"{ORGANIZATIONS_DIR_PATH}/{filename}") as org:
        data = yaml.safe_load(org)
        return render_template("organization.html", data=data)


@freezer.register_generator
def organization_page():
    organization_files = filter(lambda x: x.endswith(".yaml"), os.listdir(ORGANIZATIONS_DIR_PATH))
    for organization_file in organization_files:
        with open(f"{ORGANIZATIONS_DIR_PATH}/{organization_file}") as org:
            organization = yaml.safe_load(org)
            yield {'org_name': organization.get(ORGANIZATIONS_SLUG_FIELD_NAME)}


# Main Function, Runs at http://0.0.0.0:8000
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "build":
        freezer.freeze()
    else:
        app.run(port=8000)
