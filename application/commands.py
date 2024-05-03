import csv
import os

import requests
from flask.cli import AppGroup

from application.extensions import db
from application.models import (
    DesignCode,
    DesignCodeModel,
    DesignCodeRule,
    DesignCodeRuleModel,
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


@data_cli.command("load-data")
def load_data():
    print("Loading data")

    design_code_files_to_pydantic = {
        "design-code.csv": DesignCodeModel,
        "design-code-rule.csv": DesignCodeRuleModel,
    }
    pydantic_to_db_model = {
        DesignCodeModel: DesignCode,
        DesignCodeRuleModel: DesignCodeRule,
    }

    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(os.path.dirname(current_dir), "data")

    for filename, pydantic_model in design_code_files_to_pydantic.items():
        model = pydantic_to_db_model[pydantic_model]
        file_path = os.path.join(data_dir, filename)
        with open(file_path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                _santize(row)
                reference = row["reference"]
                if model.query.get(reference) is None:
                    org = Organisation.query.get(row["organisation"])
                    if org is None:
                        print(f"Organisation {row['organisation']} not found")
                        continue
                    try:
                        pm = pydantic_model(**row)
                        org.design_codes.append(model(**pm.model_dump()))
                        db.session.add(org)
                    except Exception as e:
                        print(f"Error with {row}")
                        print(e)
                        continue
                else:
                    print(f"Design code {reference} already in db")

        db.session.commit()

    print("Done loading data")


@data_cli.command("drop-data")
def drop_data():
    print("Dropping data")
    DesignCodeRule.query.delete()
    DesignCode.query.delete()
    print("Done dropping data")
