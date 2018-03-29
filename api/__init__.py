import os
import logging
from flask import Flask
application = Flask(__name__)

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

@application.route("/")
def hello():
    logging.info('Database: %s', os.getenv('DATABASE_URL','db url missing'))
    return "<h1'>Hello Test!</h1>"

if __name__ == "__main__":
    application.run()