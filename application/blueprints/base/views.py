import geopandas as gpd
from flask import Blueprint, render_template, request, url_for
from sqlalchemy import or_

from application.models import (
    DesignCode,
    DesignCodeArea,
    DesignCodeAreaOriginal,
    DesignCodeCharacteristic,
    DesignCodeOriginal,
    DesignCodeRule,
    DesignCodeRuleCategory,
    DesignCodeStatus,
    Organisation,
)

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


@base.route("/info")
def info():
    return render_template("info.html")


def _get_all_orgs_with_design_codes():
    dcs = DesignCode.query.all()
    organisations = set([dc.organisation for dc in dcs])
    return sorted(organisations, key=lambda org: org.name)


@base.route("/design-codes")
def design_codes():
    organisations = _get_all_orgs_with_design_codes()
    statuses = DesignCodeStatus.query.all()
    design_code_rule_categories = DesignCodeRuleCategory.query.order_by(
        DesignCodeRuleCategory.name.asc()
    ).all()

    query = DesignCode.query

    if "organisation" in request.args:
        org_selection = request.args.getlist("organisation")
        filter_condition = DesignCode.organisation_id.in_(org_selection)
        query = query.filter(filter_condition)

    if "status" in request.args:
        status_selection = request.args.getlist("status")
        filter_condition = DesignCode.design_code_status.in_(status_selection)
        query = query.filter(filter_condition)

    if "category" in request.args:
        category_selection = request.args.getlist("category")
        filter_condition = DesignCode.reference.in_(
            DesignCodeRule.query.filter(
                DesignCodeRule.design_code_rule_categories.overlap(category_selection)
            ).with_entities(DesignCodeRule.design_code_reference)
        )
        query = query.filter(filter_condition)

    dcs = query.all()

    return render_template(
        "design-codes.html",
        design_codes=dcs,
        organisations=organisations,
        filter_url=url_for("base.design_codes"),
        design_code_statuses=statuses,
        design_code_rule_categories=design_code_rule_categories,
    )


@base.route("/design-code-rules")
def design_code_rules():
    organisations = _get_all_orgs_with_design_codes()

    design_code_rule_categories = DesignCodeRuleCategory.query.order_by(
        DesignCodeRuleCategory.name.asc()
    ).all()
    design_code_characteristics = DesignCodeCharacteristic.query.order_by(
        DesignCodeCharacteristic.name.asc()
    ).all()

    query = DesignCodeRule.query

    if "organisation" in request.args:
        org_selection = request.args.getlist("organisation")
        filter_condition = DesignCodeRule.organisation_id.in_(org_selection)
        query = query.filter(filter_condition)

    if "characteristic" in request.args:
        characteristic_selection = request.args.getlist("characteristic")
        dccs = DesignCodeCharacteristic.query.filter(
            DesignCodeCharacteristic.reference.in_(characteristic_selection)
        ).all()
        rule_categories = []
        for dcc in dccs:
            rule_categories += [
                rule.reference for rule in dcc.design_code_rule_categories
            ]
        filter_condition = DesignCodeRule.design_code_rule_categories.overlap(
            rule_categories
        )
        query = query.filter(filter_condition)

    if "category" in request.args:
        category_selection = request.args.getlist("category")
        or_conditions = [
            DesignCodeRule.design_code_rule_categories.contains([term])
            for term in category_selection
        ]
        query = query.filter(or_(*or_conditions))

    design_code_rules = query.order_by(DesignCodeRule.name.asc()).all()

    filter_url = url_for("base.design_code_rules")

    return render_template(
        "design-code-rules.html",
        design_code_rules=design_code_rules,
        organisations=organisations,
        design_code_rule_categories=design_code_rule_categories,
        design_code_characteristics=design_code_characteristics,
        filter_url=filter_url,
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
        filter_condition = DesignCodeAreaOriginal.organisation_entity.in_(
            selected_org_entities
        )
        dcas = DesignCodeAreaOriginal.query.filter(filter_condition).all()
    else:
        dcas = DesignCodeAreaOriginal.query.all()

    return render_template(
        "design-code-areas.html",
        design_code_areas=dcas,
        organisations=organisations,
        filter_url=url_for("base.design_code_areas"),
    )


@base.route("/design-code/<string:reference>")
def design_code(reference):
    dc = DesignCode.query.get(reference)
    organisation = dc.organisation
    # design_code_areas = [
    #     dca
    #     for dca in DesignCodeAreaOriginal.query.all()
    #     if dca.json is not None and dca.json["design-code"] == dc.reference
    # ]
    geojson, coords, bounding_box = None, None, None
    if dc.design_code_areas:
        geojson_available = False
        # this should handle newer areas from shapefiles
        if (
            len(dc.design_code_areas) == 1
            and dc.design_code_areas[0].geojson is not None
            and dc.design_code_areas[0].geojson["type"] == "FeatureCollection"
        ):
            geojson = dc.design_code_areas[0].geojson
            geojson_available = True
        else:
            geojson = {"type": "FeatureCollection", "features": []}

            # if org boundary need uncomment this
            # for feature in organisation.geojson["features"]:
            #     geojson["features"].append(feature)

            for area in dc.design_code_areas:
                if area.geojson is not None:
                    geojson_available = True
                    geojson["features"].append(area.geojson)

        if geojson_available:
            coords, bounding_box = _get_centre_and_bounds(geojson)

    return render_template(
        "design-code.html",
        design_code=dc,
        organisation=organisation,
        design_code_areas=design_code_areas,
        geojson=geojson,
        coords=coords,
        bounding_box=bounding_box,
    )


@base.route("/design-code-rule/<reference>")
def design_code_rule(reference):
    design_code_rule = DesignCodeRule.query.get(reference)

    return render_template("design-code-rule.html", design_code_rule=design_code_rule)


@base.route("/design-code-area/<int:entity>")
def design_code_area(entity):
    dca = DesignCodeAreaOriginal.query.get(entity)
    design_code = DesignCodeOriginal.query.filter(
        DesignCodeOriginal.reference == dca.json["design-code"]
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
    geojson = {"type": "FeatureCollection", "features": []}

    dcas = DesignCodeArea.query.all()
    valid_design_code_areas = []

    for dca in dcas:
        if dca.geojson is not None and dca.geojson != "null":
            valid_design_code_areas.append(dca)
            # if geojson is featureCollection extract features
            if dca.geojson["type"] == "FeatureCollection":
                geojson["features"].extend(dca.geojson["features"])
            # else add feature to our main FeatureCollection
            else:
                geojson["features"].append(dca.geojson)

    coords, bounding_box = _get_centre_and_bounds(geojson)

    return render_template(
        "map.html",
        design_code_areas=valid_design_code_areas,
        geojson=geojson,
        coords=coords,
        bounding_box=bounding_box,
    )
