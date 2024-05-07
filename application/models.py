import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import INTEGER, JSON, Column, Date, ForeignKey, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import Mapped, mapped_column, relationship

from application.extensions import db


class Entity(db.Model):
    __abstract__ = True

    entity = Column(INTEGER, primary_key=True)
    dataset = Column(Text)
    json = Column(JSON)
    name = Column(Text)
    organisation_entity = Column(Text)
    point = Column(Text)
    prefix = Column(Text)
    reference = Column(Text)
    typology = Column(Text)
    entry_date = Column(Text)
    start_date = Column(Text)
    end_date = Column(Text)


class DesignCodeOriginal(Entity):
    __bind_key__ = "design_code"
    __tablename__ = "entity"


class DesignCodeAreaOriginal(Entity):
    __bind_key__ = "design_code_area"
    __tablename__ = "entity"

    geometry = db.Column(Text)
    geojson = db.Column(db.JSON)


class Organisation(db.Model):
    organisation: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(Text)
    prefix: Mapped[Optional[str]] = mapped_column(Text)
    reference: Mapped[Optional[str]] = mapped_column(Text)
    statistical_geography: Mapped[Optional[str]] = mapped_column(Text)
    geojson = db.Column(JSON)


class DateMixin(db.Model):
    __abstract__ = True
    start_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    end_date: Mapped[Optional[datetime.date]] = mapped_column(Date)


class DesignCode(DateMixin):
    reference: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(Text)
    description: Mapped[Optional[str]] = mapped_column(Text)
    organisation_id: Mapped[str] = mapped_column(
        ForeignKey("organisation.organisation")
    )
    organisation: Mapped["Organisation"] = relationship(backref="design_codes")
    design_code_status: Mapped[Optional[str]] = mapped_column(Text)
    documention_url: Mapped[Optional[str]] = mapped_column(Text)
    document_url: Mapped[Optional[str]] = mapped_column(Text)


class DesignCodeRule(DateMixin):
    reference: Mapped[Optional[str]] = mapped_column(Text, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(Text)
    description: Mapped[Optional[str]] = mapped_column(Text)
    design_code_categories: Mapped[Optional[list[str]]] = mapped_column(
        MutableList.as_mutable(ARRAY(Text))
    )
    organisation_id: Mapped[str] = mapped_column(
        ForeignKey("organisation.organisation")
    )
    design_code_reference: Mapped[str] = mapped_column(
        ForeignKey("design_code.reference")
    )
    design_code: Mapped["DesignCode"] = relationship(backref="design_code_rules")
    documentation_url: Mapped[Optional[str]] = mapped_column(Text)
    document_url: Mapped[Optional[str]] = mapped_column(Text)


class DesignCodeArea(DateMixin):
    reference: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(Text)
    geometry: Mapped[Optional[str]] = mapped_column(Text)
    point: Mapped[Optional[str]] = mapped_column(Text)
    organisation_id: Mapped[str] = mapped_column(
        ForeignKey("organisation.organisation")
    )
    organisation: Mapped["Organisation"] = relationship(backref="design_code_areas")
    design_code_area_type: Mapped[Optional[str]] = mapped_column(Text)
    design_code_reference: Mapped[str] = mapped_column(
        ForeignKey("design_code.reference")
    )
    design_code: Mapped["DesignCode"] = relationship(backref="design_code_areas")
    design_code_rules: Mapped[Optional[str]] = mapped_column(Text)
    documentation_url: Mapped[Optional[str]] = mapped_column(Text)
    document_url: Mapped[Optional[str]] = mapped_column(Text)


class DesignCodeCharacteristic(db.Model):
    reference: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(Text)


class DesignCodeCategory(db.Model):
    reference: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(Text)
    design_code_characteristic_reference: Mapped[str] = mapped_column(
        ForeignKey("design_code_characteristic.reference")
    )
    design_code_charactersitic: Mapped["DesignCodeCharacteristic"] = relationship(
        backref="design_code_categories"
    )


# class DesignCodeAreaType:
#     pass


# class DesignCodeStatus:
#     pass


# pydantic models


class DesignCodeModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    reference: str
    name: str
    description: Optional[str]
    organisation_id: str = Field(alias="organisation")
    design_code_status: Optional[str] = Field(alias="design-code-status")
    documention_url: Optional[str] = Field(alias="documention-url")
    document_url: Optional[str] = Field(alias="document-url")
    start_date: Optional[datetime.date] = Field(alias="start-date")
    end_date: Optional[datetime.date] = Field(alias="end-date")


class DesignCodeRuleModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    reference: str
    name: Optional[str]
    description: Optional[str]
    design_code_categories: Optional[list[str]] = Field(alias="design-code-categories")
    organisation_id: str = Field(alias="organisation")
    design_code_reference: str = Field(alias="design-code")
    documentation_url: Optional[str] = Field(alias="documentation-url")
    document_url: Optional[str] = Field(alias="document-url")

    @field_validator("design_code_categories", mode="before")
    @classmethod
    def validate_design_code_categories(cls, value: str) -> list[str]:
        if value:
            categories = value.split(";")
            if isinstance(categories, list):
                return categories
            categories = value.split(",")
            if isinstance(categories, list):
                return categories
        else:
            None


class DesignCodeCharacteristicModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    reference: str
    name: Optional[str]


class DesignCodeCategoryModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    reference: str
    name: Optional[str]
    design_code_characteristic_reference: str = Field(
        alias="design-code-characteristic"
    )
