from flask import Blueprint, render_template

from application.models import DesignCodeArea, DesignCodes

base = Blueprint("base", __name__)


@base.route("/")
def index():
    design_codes = DesignCodes.query.all()
    design_code_areas = DesignCodeArea.query.all()
    return render_template(
        "index.html", design_codes=design_codes, design_code_areas=design_code_areas
    )
