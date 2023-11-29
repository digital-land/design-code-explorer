import geopandas as gpd
from flask import Blueprint, render_template, request, url_for

from application.models import DesignCode, DesignCodeArea, Organisation

base = Blueprint("base", __name__)


def _get_centre_and_bounds(geojson):
    if geojson is not None:
        gdf = gpd.GeoDataFrame.from_features(geojson["features"])
        bounding_box = list(gdf.total_bounds)
        return {"lat": gdf.centroid.y[0], "long": gdf.centroid.x[0]}, bounding_box
    return None, None


@base.route("/")
def index():
    return render_template("index.html")


@base.route("/design-codes")
def design_codes():
    organisations = Organisation.query.all()

    if "organisation" in request.args:
        selection = request.args.getlist("organisation")
        orgs = [
            Organisation.query.filter(Organisation.reference == ref).first()
            for ref in selection
        ]
        selected_org_entities = [org.organisation for org in orgs]
        filter_condition = DesignCode.organisation_entity.in_(selected_org_entities)
        dcs = DesignCode.query.filter(filter_condition).all()
    else:
        dcs = DesignCode.query.all()

    return render_template(
        "design-codes.html",
        design_codes=dcs,
        organisations=organisations,
        filter_url=url_for("base.design_codes"),
    )


@base.route("/design-code-areas")
def design_code_areas():
    organisations = Organisation.query.all()

    if "organisation" in request.args:
        selection = request.args.getlist("organisation")
        orgs = [
            Organisation.query.filter(Organisation.reference == ref).first()
            for ref in selection
        ]
        selected_org_entities = [org.organisation for org in orgs]
        filter_condition = DesignCodeArea.organisation_entity.in_(selected_org_entities)
        dcas = DesignCodeArea.query.filter(filter_condition).all()
    else:
        dcas = DesignCodeArea.query.all()

    return render_template(
        "design-code-areas.html",
        design_code_areas=dcas,
        organisations=organisations,
        filter_url=url_for("base.design_code_areas"),
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
    if design_code_areas:
        geojson = {"type": "FeatureCollection", "features": []}

        # if org boundary need uncomment this
        # for feature in organisation.geojson["features"]:
        #     geojson["features"].append(feature)

        for area in design_code_areas:
            geojson["features"].append(area.geojson)

        coords, bounding_box = _get_centre_and_bounds(geojson)
    else:
        geojson, coords, bounding_box = None, None, None

    return render_template(
        "design-code.html",
        design_code=dc,
        organisation=organisation,
        design_code_areas=design_code_areas,
        geojson=geojson,
        coords=coords,
        bounding_box=bounding_box,
    )


@base.route("/design-code-area/<int:entity>")
def design_code_area(entity):
    dca = DesignCodeArea.query.get(entity)
    design_code = DesignCode.query.filter(
        DesignCode.reference == dca.json["design-code"]
    ).first()
    organisation = Organisation.query.get(dca.organisation_entity)

    # in development plan geography we do coords, bounding_box = _get_centre_and_bounds(development_plan.geography)
    # but this fails here because it doesn't have a 'features' key
    # coords, bounding_box = _get_centre_and_bounds(dca)

    geojson = {"type": "FeatureCollection", "features": []}

    # if org boundary need uncomment this
    # for feature in organisation.geojson["features"]:
    #     geojson["features"].append(feature)

    geojson["features"].append(dca.geojson)
    coords, bounding_box = _get_centre_and_bounds(geojson)
    return render_template(
        "design-code-area.html",
        design_code_area=dca,
        organisation=organisation,
        design_code=design_code,
        geojson=geojson,
        coords=coords,
        bounding_box=bounding_box,
    )


@base.route("/map")
def map():
    design_code_areas = DesignCodeArea.query.all()
    geojson = {"type": "FeatureCollection", "features": []}

    for dca in design_code_areas:
        geojson["features"].append(dca.geojson)

    coords, bounding_box = _get_centre_and_bounds(geojson)

    return render_template(
        "map.html",
        design_code_areas=design_code_areas,
        geojson=geojson,
        coords=coords,
        bounding_box=bounding_box,
    )
