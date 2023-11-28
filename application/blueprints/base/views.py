from flask import Blueprint, render_template

from application.models import DesignCode, Organisation

base = Blueprint("base", __name__)


@base.route("/")
def index():
    design_codes = DesignCode.query.all()

    return render_template("index.html", design_codes=design_codes)


@base.route("/design-code/<int:entity>")
def design_code(entity):
    design_code = DesignCode.query.get(entity)
    organisation = Organisation.query.get(design_code.organisation_entity)
    return render_template(
        "design-code.html", design_code=design_code, organisation=organisation
    )
