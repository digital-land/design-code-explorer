import geopandas as gpd
from flask import Blueprint, render_template

from application.models import DesignCode, DesignCodeArea, Organisation

base = Blueprint("base", __name__)


def _get_centre_and_bounds(geography):
    if geography is not None:
        gdf = gpd.GeoDataFrame.from_features(geography.geojson["features"])
        bounding_box = list(gdf.total_bounds)
        return {"lat": gdf.centroid.y[0], "long": gdf.centroid.x[0]}, bounding_box
    return None, None


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
    # TODO I'm not sure how to make the FeatureCollection or whatever I need to make to pass to this func
    # in development plan it was a single geography whereas here is could be multiple
    # coords, bounding_box = _get_centre_and_bounds(????)
    coords = {"lat": 52.561928, "long": -1.464854}
    bbox = []
    return render_template(
        "design-code.html",
        design_code=dc,
        organisation=organisation,
        design_code_areas=design_code_areas,
        coords=coords,
        bbox=bbox,
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
