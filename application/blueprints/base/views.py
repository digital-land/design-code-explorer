from flask import Blueprint, render_template

from application.models import DesignCode, DesignCodeArea, Organisation

base = Blueprint("base", __name__)


@base.route("/")
def index():
    return render_template("index.html")


@base.route("/design-codes")
def design_codes():
    dcs = DesignCode.query.all()
    organisations = Organisation.query.all()
    return render_template(
        "design-codes.html", design_codes=dcs, organisations=organisations
    )


@base.route("/design-code-areas")
def design_code_areas():
    dcas = DesignCodeArea.query.all()
    organisations = Organisation.query.all()
    return render_template(
        "design-code-areas.html",
        design_code_areas=dcas,
        organisations=organisations,
    )


@base.route("/design-code/<int:entity>")
def design_code(entity):
    dc = DesignCode.query.get(entity)
    organisation = Organisation.query.get(dc.organisation_entity)
    design_code_areas = [
        dca
        for dca in DesignCodeArea.query.all()
        if dca.json is not None and dca.json["design-code"] == dc.reference
    ]
    return render_template(
        "design-code.html",
        design_code=dc,
        organisation=organisation,
        design_code_areas=design_code_areas,
    )


@base.route("/design-code-area/<int:entity>")
def design_code_area(entity):
    dca = DesignCodeArea.query.get(entity)
    design_code = DesignCode.query.filter(
        DesignCode.reference == dca.json["design-code"]
    ).first()
    organisation = Organisation.query.get(dca.organisation_entity)
    return render_template(
        "design-code-area.html",
        design_code_area=dca,
        organisation=organisation,
        design_code=design_code,
    )
