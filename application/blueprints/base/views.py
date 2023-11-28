from flask import Blueprint, render_template, request

from application.models import DesignCode, DesignCodeArea, Organisation

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


@base.route("/design-code-area")
def design_code_area():
    design_code_reference = request.args.get("design_code_reference")
    design_code_areas = [
        dca
        for dca in DesignCodeArea.query.all()
        if dca.json is not None and dca.json["design-code"] == design_code_reference
    ]
    return render_template("design-code-area.html", design_code_areas=design_code_areas)
