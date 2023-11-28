from application.extensions import db


class Entity(db.Model):
    __abstract__ = True

    entity = db.Column(db.INTEGER, primary_key=True)
    dataset = db.Column(db.TEXT)
    json = db.Column(db.JSON)
    name = db.Column(db.TEXT)
    organisation_entity = db.Column(db.TEXT)
    point = db.Column(db.TEXT)
    prefix = db.Column(db.TEXT)
    reference = db.Column(db.TEXT)
    typology = db.Column(db.TEXT)
    entry_date = db.Column(db.TEXT)
    start_date = db.Column(db.TEXT)
    end_date = db.Column(db.TEXT)


class DesignCode(Entity):
    __tablename__ = "entity"


class DesignCodeArea(Entity):
    __bind_key__ = "design_code_area"
    __tablename__ = "entity"

    geometry = db.Column(db.TEXT)
