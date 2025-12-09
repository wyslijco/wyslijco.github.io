import os
import sys

import yaml
from flask import Flask, abort, render_template, send_from_directory, url_for
from flask_frozen import Freezer  # Added

from config import ORGANIZATIONS_DIR_PATH, ORGANIZATIONS_SLUG_FIELD_NAME

DEBUG = True
FREEZER_DESTINATION = "../_site"  # builds to the default desitination for GitHub Pages

app = Flask(__name__)
app.config.from_object(__name__)
freezer = Freezer(app)


def trim_strings(data):
    """Recursively trim trailing/leading spaces from all string values in nested data structures."""
    if isinstance(data, dict):
        return {key: trim_strings(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [trim_strings(item) for item in data]
    elif isinstance(data, str):
        return data.strip()
    else:
        return data


def get_organizations() -> dict[str, str]:
    organization_files = filter(
        lambda x: x.endswith(".yaml"), os.listdir(ORGANIZATIONS_DIR_PATH)
    )
    organizations = dict()
    for organization_file in organization_files:
        with open(f"{ORGANIZATIONS_DIR_PATH}/{organization_file}") as org:
            organization = trim_strings(yaml.safe_load(org))
            organizations[organization.get(ORGANIZATIONS_SLUG_FIELD_NAME)] = (
                organization_file
            )
    return organizations


organizations: dict[str, str] = get_organizations()


def static_file(name: str):
    dir_path = os.path.join(app.root_path, "statics")
    return send_from_directory(
        dir_path,
        name,
    )


def get_static_files_list():
    current_file_directory = os.path.dirname(os.path.abspath(__file__))
    return os.listdir(os.path.join(current_file_directory, "statics"))


for filename in get_static_files_list():
    app.route(f"/{filename}", strict_slashes=False, endpoint=filename)(
        lambda f=filename: static_file(f)
    )


@freezer.register_generator
def generate_favicon_statics():
    path = os.path.join(app.root_path, "statics")
    files = os.listdir(path)
    for static in files:
        yield url_for(static)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


# Generated css
@app.route("/output.css")
def outputCss():
    return send_from_directory(
        app.root_path,
        "output.css",
    )


@app.route("/", strict_slashes=False)
def index():
    # Load organization data for the rotating links
    org_data = []
    for org_slug, filename in organizations.items():
        with open(f"{ORGANIZATIONS_DIR_PATH}/{filename}") as org:
            data = trim_strings(yaml.safe_load(org))
            org_data.append({
                'adres': org_slug,
                'nazwa': data.get('nazwa')
            })

    return render_template("index.html", organizations=org_data)


@app.route("/info/", strict_slashes=False)
def info():
    return render_template("info.html")


@app.route("/organizacje/", strict_slashes=False)
def organizations_list():
    # Load all organization data for the list
    org_data = []
    for org_slug, filename in organizations.items():
        with open(f"{ORGANIZATIONS_DIR_PATH}/{filename}") as org:
            data = trim_strings(yaml.safe_load(org))
            org_data.append({
                'adres': org_slug,
                'nazwa': data.get('nazwa')
            })

    # Sort organizations alphabetically by name
    org_data.sort(key=lambda x: x['nazwa'])

    return render_template("organizations.html", organizations=org_data)


@app.route("/<string:org_name>/", strict_slashes=False)
def organization_page(org_name):
    filename = organizations.get(org_name)
    if not filename:
        abort(404)
    with open(f"{ORGANIZATIONS_DIR_PATH}/{filename}") as org:
        data = trim_strings(yaml.safe_load(org))
        if not data["produkty"]:
            data["produkty"] = []
        return render_template("organization.html", data=data)


@freezer.register_generator
def organization_page():
    organization_files = filter(
        lambda x: x.endswith(".yaml"), os.listdir(ORGANIZATIONS_DIR_PATH)
    )
    for organization_file in organization_files:
        with open(f"{ORGANIZATIONS_DIR_PATH}/{organization_file}") as org:
            organization = trim_strings(yaml.safe_load(org))
            yield {"org_name": organization.get(ORGANIZATIONS_SLUG_FIELD_NAME)}


# Main Function, Runs at http://0.0.0.0:8000
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "build":
        freezer.freeze()
    else:
        app.run(host='0.0.0.0', port=8000)
