import os
import sys

from flask import Flask, abort, render_template, send_from_directory, url_for
from flask_frozen import Freezer, redirect  # Added

from organizations import get_organization_data, get_organizations, Organization

DEBUG = True
FREEZER_DESTINATION = "../_site"  # builds to the default desitination for GitHub Pages

app = Flask(__name__)
app.config.from_object(__name__)
freezer = Freezer(app)


organizations, slug_to_organization = get_organizations()


def static_file(name: str):
    dir_path = os.path.join(app.root_path, "statics")
    return send_from_directory(
        dir_path,
        name,
    )


def get_static_files_list():
    current_file_directory = os.path.dirname(os.path.abspath(__file__))
    return os.listdir(os.path.join(current_file_directory, "statics"))


for static_filename in get_static_files_list():
    app.route(f"/{static_filename}", strict_slashes=False, endpoint=static_filename)(
        lambda f=static_filename: static_file(f)
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
    org_data = list(organizations.values())
    return render_template("index.html", organizations=org_data)


@app.route("/info/", strict_slashes=False)
def info():
    return render_template("info.html")


@app.route("/organizacje/", strict_slashes=False)
def organizations_list():
    org_data = sorted(list(organizations.values()), key=lambda x: x.name)
    return render_template("organizations.html", organizations=org_data)


@app.route("/dodaj/", strict_slashes=False)
def join():
    return render_template("join.html")


@app.route("/<string:org_name>/", strict_slashes=False)
def organization_page(org_name):
    if org_name not in slug_to_organization:
        abort(404)

    org: Organization = slug_to_organization[org_name]
    if org_name != org.slugs[0]:
        return redirect(url_for("organization_page", org_name=org.slugs[0]))

    filename = org.file
    if not filename:
        abort(404)

    return render_template("organization.html", data=get_organization_data(org))


@freezer.register_generator
def organization_page():  # noqa: F811
    for slug, filename in slug_to_organization.items():
        yield {"org_name": slug}


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "build":
        freezer.freeze()
    else:
        app.run(host="0.0.0.0", port=8000)
