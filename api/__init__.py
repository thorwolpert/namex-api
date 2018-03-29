import os
import logging
from flask import Flask
from config import Config

application = Flask(__name__)
application.config.from_object(Config)

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

@application.route("/")
def hello():
    logging.info('Database: %s', Config.SQLALCHEMY_DATABASE_URI)
    return "<h1'>Hello Test!</h1>"

if __name__ == "__main__":
    application.run()