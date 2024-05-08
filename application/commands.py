import csv
import json
import os

import requests
from flask.cli import AppGroup

from application.extensions import db
from application.models import (
    DesignCode,
    DesignCodeArea,
    DesignCodeAreaModel,
    DesignCodeAreaOriginal,
    DesignCodeAreaType,
    DesignCodeAreaTypeModel,
    DesignCodeCharacteristic,
    DesignCodeCharacteristicModel,
    DesignCodeModel,
    DesignCodeOriginal,
    DesignCodeRule,
    DesignCodeRuleCategory,
    DesignCodeRuleCategoryModel,
    DesignCodeRuleModel,
    DesignCodeStatus,
    DesignCodeStatusModel,
    Organisation,
)

data_cli = AppGroup("data")


def paginate(url):
    items = []
    while url:
        response = requests.get(url)
        try:
            url = response.links.get("next").get("url")
        except AttributeError:
            url = None
        items.extend(response.json()["rows"])
    return items


@data_cli.command("load-orgs")
def load_org_db():
    print("Loading organisation db")
    organisation_url = "https://datasette.planning.data.gov.uk/digital-land/organisation.json?_shape=objects"
    # resp = requests.get(organisation_url)
    data = paginate(organisation_url)
    for org in data:
        name = org["name"]
        organisation = org["organisation"]
        prefix = org["prefix"]
        reference = org["reference"]
        statistical_geography = org["statistical_geography"]
        if statistical_geography:
            geojson_url = f"https://www.planning.data.gov.uk/entity.geojson?curie=statistical-geography:{statistical_geography}"  # noqa
            resp = requests.get(geojson_url)
            geojson = resp.json()
            if geojson == "null":
                geojson = None
        else:
            geojson = None

        if not Organisation.query.get(organisation):
            print(f"Adding organisation {organisation}")
            org = Organisation(
                organisation=organisation,
                name=name,
                prefix=prefix,
                reference=reference,
                statistical_geography=statistical_geography,
                geojson=geojson,
            )
            db.session.add(org)
            db.session.commit()
        else:
            print(f"Organisation {organisation} already in db")

    print("Done loading organisation db")


def _santize(row):
    for key, val in row.items():
        if val == "":
            row[key] = None


@data_cli.command("load")
def load_data():
    print("Loading data")

    base_url = "https://dluhc-datasets.planning-data.dev/dataset"

    design_code_files_to_pydantic = {
        f"{base_url}/design-code-characteristic.json": DesignCodeCharacteristicModel,
        f"{base_url}/design-code-rule-category.json": DesignCodeRuleCategoryModel,
        f"{base_url}/design-code-area-type.json": DesignCodeAreaTypeModel,
        f"{base_url}/design-code-status.json": DesignCodeStatusModel,
        "design-code.csv": DesignCodeModel,
        "design-code-rule.csv": DesignCodeRuleModel,
        "design-code-area.csv": DesignCodeAreaModel,
    }

    pydantic_to_db_model = {
        DesignCodeModel: DesignCode,
        DesignCodeRuleModel: DesignCodeRule,
        DesignCodeCharacteristicModel: DesignCodeCharacteristic,
        DesignCodeRuleCategoryModel: DesignCodeRuleCategory,
        DesignCodeAreaTypeModel: DesignCodeAreaType,
        DesignCodeStatusModel: DesignCodeStatus,
        DesignCodeAreaModel: DesignCodeArea,
    }

    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(current_dir), "data")

    for location, pydantic_model in design_code_files_to_pydantic.items():
        model = pydantic_to_db_model[pydantic_model]
        rows = []
        if location.startswith("https"):
            print(f"Loading data from {location}")
            resp = requests.get(location)
            rows = resp.json()["records"]
        else:
            file_path = os.path.join(data_dir, location)
            print(f"Loading data from {location}")
            with open(file_path, "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    rows.append(row)
        for row in rows:
            _santize(row)
            reference = row["reference"]
            if model.query.get(reference) is None:
                try:
                    pm = pydantic_model(**row)
                    m = model(**pm.model_dump())
                    if location == "design-code-area.csv":
                        geojson_path = os.path.join(data_dir, f"{reference}.geojson")
                        if os.path.exists(geojson_path):
                            with open(geojson_path, "r") as f:
                                geojson = json.load(f)
                                m.geojson = geojson
                    db.session.add(m)
                    db.session.commit()
                except Exception as e:
                    print(f"Error with {row}")
                    print(e)
                    continue
            else:
                print(f"{reference} from {location} already in db")

    print("Done loading data")


@data_cli.command("drop")
def drop_data():
    print("Dropping data")

    for table in reversed(db.metadata.sorted_tables):
        if table.name != "organisation":
            print(f"Delete all from {table.name}")
            db.session.execute(table.delete())
            db.session.commit()

    print("Done dropping data")


@data_cli.command("merge")
def merge_data():
    print("Merging data from sqlite db to postgres db")
    base_url = "https://datasette.planning.data.gov.uk/entity/entity.json"
    org_url = "{base_url}?_sort=entity&entity__exact={org_entity}&_shape=array"
    orgs = {}
    for design_code in DesignCodeOriginal.query.all():
        org_entity = design_code.organisation_entity
        resp = requests.get(org_url.format(base_url=base_url, org_entity=org_entity))
        prefix = resp.json()[0]["prefix"]
        reference = resp.json()[0]["reference"]
        org = f"{prefix}:{reference}"

        organisation = Organisation.query.get(org)
        if organisation is None:
            print(f"can't add design code, {org} not found")
        else:
            data = design_code.dict()
            data["organisation_id"] = organisation.organisation
            dc = DesignCode.query.get(data["reference"])
            if dc is None:
                dc = DesignCode(**data)
                db.session.add(dc)
                db.session.commit()
            else:
                print(f"Design code {dc.reference} already in db")

            orgs[org_entity] = organisation
            print(f"Merged design code {dc.reference}")

    for design_code_area in DesignCodeAreaOriginal.query.all():
        org_entity = design_code_area.organisation_entity
        organisation = orgs.get(org_entity, None)
        if organisation is None:
            print(f"can't add design code area, {org_entity} not found")
        else:
            data = design_code_area.dict()
            data["organisation_id"] = organisation.organisation
            dca = DesignCodeArea.query.get(data["reference"])
            if dca is None:
                ref = data["design_code"]
                data["design_code_reference"] = ref
                del data["design_code"]
                dca = DesignCodeArea(**data)
                db.session.add(dca)
                db.session.commit()
            else:
                print(f"Design code area {dca.reference} already in db")

            print(f"Merged design code area {dca.reference}")

    print("Done merging data")
