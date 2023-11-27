from flask import Blueprint, render_template

base = Blueprint("base", __name__)


@base.route("/design-code")
def index():
    return render_template("index.html")
