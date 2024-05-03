# -*- coding: utf-8 -*-
import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    APP_ROOT = os.path.abspath(os.path.dirname(__file__))
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_ROOT, os.pardir))
    SECRET_KEY = os.getenv("SECRET_KEY")
    DATABASE_URL = os.getenv("DATABASE_URL")
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_BINDS = {
        "design_code": f"sqlite:///{PROJECT_ROOT}/data/design-code.sqlite3",
        "design_code_area": f"sqlite:///{PROJECT_ROOT}/data/design-code-area.sqlite3",
        "organisation": f"sqlite:///{PROJECT_ROOT}/data/organisation.sqlite3",
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = False
    DEBUG = False


class DevelopmentConfig(Config):
    ENV = "development"
    DEBUG = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_RECORD_QUERIES = True


class TestConfig(Config):
    ENV = "test"
    DEBUG = True
    TESTING = True
