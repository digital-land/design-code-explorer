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

    def dict(self):
        data = {}
        for key, val in self.json.items():
            k = key.replace("-", "_")
            if val == "":
                data[k] = None
            else:
                data[k] = val

        return {
            "entity": self.entity if self.entity else None,
            "name": self.name if self.name else None,
            "prefix": self.prefix if self.prefix else None,
            "reference": self.reference if self.reference else None,
            "entry_date": self.entry_date if self.entry_date else None,
            "start_date": self.start_date if self.start_date else None,
            "end_date": self.end_date if self.end_date else None,
            **data,
        }


class DesignCodeOriginal(Entity):
    __bind_key__ = "design_code"
    __tablename__ = "entity"


class DesignCodeAreaOriginal(Entity):
    __bind_key__ = "design_code_area"
    __tablename__ = "entity"

    geometry = db.Column(Text)
    geojson = db.Column(db.JSON)

    def dict(self):
        data = super().dict()
        data["geometry"] = self.geometry if self.geometry else None
        data["geojson"] = self.geojson if self.geojson else None
        return data


class Organisation(db.Model):
    organisation: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(Text)
    prefix: Mapped[Optional[str]] = mapped_column(Text)
    reference: Mapped[Optional[str]] = mapped_column(Text)
    statistical_geography: Mapped[Optional[str]] = mapped_column(Text)
    geojson = db.Column(JSON)


class DateMixin(db.Model):
    __abstract__ = True

    entry_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    start_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    end_date: Mapped[Optional[datetime.date]] = mapped_column(Date)


class DesignCode(DateMixin):
    reference: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(Text)
    entity: Mapped[Optional[int]] = mapped_column(INTEGER)
    prefix: Mapped[Optional[str]] = mapped_column(Text)
    description: Mapped[Optional[str]] = mapped_column(Text)
    organisation_id: Mapped[str] = mapped_column(
        ForeignKey("organisation.organisation")
    )
    organisation: Mapped["Organisation"] = relationship(backref="design_codes")
    design_code_status: Mapped[Optional[str]] = mapped_column(Text)
    documentation_url: Mapped[Optional[str]] = mapped_column(Text)
    document_url: Mapped[Optional[str]] = mapped_column(Text)


class DesignCodeRule(DateMixin):
    reference: Mapped[Optional[str]] = mapped_column(Text, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(Text)
    entity: Mapped[Optional[int]] = mapped_column(INTEGER)
    prefix: Mapped[Optional[str]] = mapped_column(Text)
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
    entity: Mapped[Optional[int]] = mapped_column(INTEGER)
    prefix: Mapped[Optional[str]] = mapped_column(Text)
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
    geojson = db.Column(JSON)


class DesignCodeCharacteristic(DateMixin):
    reference: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(Text)
    entity: Mapped[Optional[int]] = mapped_column(INTEGER)
    prefix: Mapped[Optional[str]] = mapped_column(Text)


class DesignCodeRuleCategory(DateMixin):
    reference: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(Text)
    design_code_characteristic_reference: Mapped[str] = mapped_column(
        ForeignKey("design_code_characteristic.reference")
    )
    design_code_charactersitic: Mapped["DesignCodeCharacteristic"] = relationship(
        backref="design_code_rule_categories"
    )
    entity: Mapped[Optional[int]] = mapped_column(INTEGER)
    prefix: Mapped[Optional[str]] = mapped_column(Text)


class DesignCodeAreaType(DateMixin):
    reference: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(Text)
    description: Mapped[Optional[str]] = mapped_column(Text)
    entity: Mapped[Optional[int]] = mapped_column(INTEGER)
    prefix: Mapped[Optional[str]] = mapped_column(Text)


class DesignCodeStatus(DateMixin):
    reference: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(Text)
    entity: Mapped[Optional[int]] = mapped_column(INTEGER)
    prefix: Mapped[Optional[str]] = mapped_column(Text)


# pydantic models


class DesignCodeModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    reference: str
    name: Optional[str]
    prefix: Optional[str]
    entity: Optional[int]
    description: Optional[str]
    organisation_id: str = Field(alias="organisation")
    design_code_status: Optional[str] = Field(alias="design-code-status")
    documention_url: Optional[str] = Field(alias="documention-url")
    document_url: Optional[str] = Field(alias="document-url")
    start_date: Optional[datetime.date] = Field(alias="start-date")
    end_date: Optional[datetime.date] = Field(alias="end-date")
    entry_date: Optional[datetime.date] = Field(alias="entry-date")


class DesignCodeRuleModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    reference: str
    name: Optional[str]
    prefix: Optional[str]
    entity: Optional[int]
    description: Optional[str]
    design_code_categories: Optional[list[str]] = Field(alias="design-code-categories")
    organisation_id: str = Field(alias="organisation")
    design_code_reference: str = Field(alias="design-code")
    documentation_url: Optional[str] = Field(alias="documentation-url")
    document_url: Optional[str] = Field(alias="document-url")
    start_date: Optional[datetime.date] = Field(alias="start-date")
    end_date: Optional[datetime.date] = Field(alias="end-date")
    entry_date: Optional[datetime.date] = Field(alias="entry-date")

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
    prefix: Optional[str]
    entity: Optional[int]
    start_date: Optional[datetime.date] = Field(alias="start-date")
    end_date: Optional[datetime.date] = Field(alias="end-date")
    entry_date: Optional[datetime.date] = Field(alias="entry-date")


class DesignCodeRuleCategoryModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    reference: str
    name: Optional[str]
    prefix: Optional[str]
    entity: Optional[int]
    design_code_characteristic_reference: str = Field(
        alias="design-code-characteristic"
    )
    start_date: Optional[datetime.date] = Field(alias="start-date")
    end_date: Optional[datetime.date] = Field(alias="end-date")
    entry_date: Optional[datetime.date] = Field(alias="entry-date")


class DesignCodeAreaTypeModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    reference: str
    name: Optional[str]
    prefix: Optional[str]
    entity: Optional[int]
    description: Optional[str]
    start_date: Optional[datetime.date] = Field(alias="start-date")
    end_date: Optional[datetime.date] = Field(alias="end-date")
    entry_date: Optional[datetime.date] = Field(alias="entry-date")


class DesignCodeStatusModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    reference: str
    name: Optional[str]
    prefix: Optional[str]
    entity: Optional[int]
    start_date: Optional[datetime.date] = Field(alias="start-date")
    end_date: Optional[datetime.date] = Field(alias="end-date")
    entry_date: Optional[datetime.date] = Field(alias="entry-date")
