from flask import jsonify
from app import api


@api.route("/healthz")
def healthz():
    # TODO: add a poll to the DB when called
    return jsonify({'message': 'api is healthy'}), 200


@api.route("/readyz")
def readyz():
    # TODO: add a poll to the DB when called
    return jsonify({'message': 'api is ready'}), 200
