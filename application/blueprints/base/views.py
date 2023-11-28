from flask import Blueprint, render_template

from application.models import DesignCode, DesignCodeArea

base = Blueprint("base", __name__)


@base.route("/")
def index():
    design_codes = DesignCode.query.all()
    design_code_areas = DesignCodeArea.query.all()
    return render_template(
        "index.html", design_codes=design_codes, design_code_areas=design_code_areas
    )


@base.route("/design-code/<int:entity>")
def design_code(entity):
    design_code = DesignCode.query.get(entity)
    return render_template("design-code.html", design_code=design_code)
