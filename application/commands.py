import os

import requests
from flask.cli import AppGroup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from application.models import DesignCode, DesignCodeArea, Organisation

data_cli = AppGroup("data")


@data_cli.command("create-org-db")
def create_org_db():
    db_path = os.path.join("data", "organisation.sqlite3")
    print("Creating organisation db at", db_path)
    engine = create_engine(f"sqlite:///{db_path}")
    Session = sessionmaker(bind=engine)
    session = Session()  # noqa
    Organisation.__table__.create(bind=engine, checkfirst=True)


@data_cli.command("load-orgs")
def load_org_db():
    from application.extensions import db

    print("Loading organisation db")
    org_entity_url = "https://www.planning.data.gov.uk/entity/{org_entity}.json"

    for design_code in DesignCode.query.all():
        url = org_entity_url.format(org_entity=design_code.organisation_entity)
        resp = requests.get(url)
        data = resp.json()
        organisation = data["entity"]
        name = data["name"]
        prefix = data["prefix"]
        reference = data["reference"]
        statistical_geography = data["statistical-geography"]

        geojson_url = f"https://www.planning.data.gov.uk/entity.geojson?curie=statistical-geography:{statistical_geography}"  # noqa

        resp = requests.get(geojson_url)
        geojson = resp.json()

        if not Organisation.query.get(design_code.organisation_entity):
            print(f"Adding organisation {design_code.organisation_entity}")
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
            print(f"Added organisation {design_code.organisation_entity}")
        else:
            print(f"Organisation {design_code.organisation_entity} already exists")

    print("Done loading organisation db")


@data_cli.command("area-geojson")
def get_area_geojson():
    from application.extensions import db

    geojson_url = "https://www.planning.data.gov.uk/entity/{entity}.geojson"
    for area in DesignCodeArea.query.all():
        url = geojson_url.format(entity=area.entity)
        try:
            resp = requests.get(url)
            geojson = resp.json()
            area.geojson = geojson
            db.session.add(area)
            db.session.commit()
            print(f"Added geojson for {area.entity}")
        except Exception:
            print(f"Failed to add geojson for {area.entity}: url {url}")
