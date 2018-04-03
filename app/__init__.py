# -*- coding: utf-8 -*-
"""NAMEX API

This module is the API for the Names Examination system

TODO: Fill more of this in
"""
import logging
from flask import Flask
from flask_restplus import Api
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_migrate import Migrate


application = Flask(__name__)
application.config.from_object(Config)
api = Api(application, prefix='/api/v1')

db = SQLAlchemy(application)
migrate = Migrate(application, db)

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

# noinspection PyPep8
from app.models.request import Request
# noinspection PyPep8
from app.resources.requests import Request


if __name__ == "__main__":
    application.run()
