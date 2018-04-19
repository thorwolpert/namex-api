"""Requests used to support the namex API

TODO: Fill in a larger description once the API is defined for V1
"""
from flask import request, jsonify, g # _request_ctx_stack
from flask_restplus import Resource, fields, cors
from marshmallow import ValidationError
from app import api, auth_services, oidc
from sqlalchemy import exc
from app.utils.util import cors_preflight
import logging

from app.auth_services import AuthError
from app.models.request import Request as RequestDAO, RequestsSchema

request_schema = RequestsSchema(many=False)
request_schemas = RequestsSchema(many=True)

@cors_preflight("GET")
@api.route('/requests/queues/@me/oldest', methods=['GET','OPTIONS'])
class RequestsQueue(Resource):
    """Acting like a QUEUE this gets the next NR (just the NR number)
    and assigns it to your auth id
    """

    # noinspection PyUnusedLocal,PyUnusedLocal
    @staticmethod
    @cors.crossdomain(origin='*')
    # @auth_services.requires_auth
    @oidc.accept_token(require_token=True)
    def get():
        try:
            user = g.oidc_token_info['username']
            nr = RequestDAO.get_queued_oldest(user) #_request_ctx_stack.top.current_user['sub'])
        except exc.SQLAlchemyError as err:
            #TODO should put some span trace on the error message
            logging.log(logging.ERROR, 'error in getting next NR. {}'.format(err))
            return {"message": "An error occurred getting the next Name Request."}, 500
        except AttributeError as err:
            return {"message": "There are no Name Requests to work on."}, 404

        return '{{"nameRequest": "{0}" }}'.format(nr), 200


@cors_preflight("POST")
@api.route('/requests', methods=['POST', 'OPTIONS'])
class Requests(Resource):
    a_request = api.model('Request', {'submitter': fields.String('The submitter name'),
                                      'corpType': fields.String('The corporation type'),
                                      'reqType': fields.String('The name request type')
                                      })

    @api.errorhandler(AuthError)
    def handle_auth_error(ex):
        # response = jsonify(ex.error)
        # response.status_code = ex.status_code
        # return response, 401
        return {}, 401

    # noinspection PyUnusedLocal,PyUnusedLocal
    @api.expect(a_request)
    @cors.crossdomain(origin='*')
    # @auth_services.requires_auth
    @oidc.accept_token(require_token=True)
    def post(self, *args, **kwargs):

        json_input = request.get_json()
        if not json_input:
            return {'message': 'No input data provided'}, 400

        try:
            data = request_schema.load(json_input)
        except ValidationError as err:
            return jsonify({'errors': err.messages}), 422

        nrd = RequestDAO(submitter=data[0].submitter, corpType=data[0].corpType, reqType=data[0].reqType)

        try:
            nrd.save_to_db()
            message = 'Successfully created Name Request: {0}'.format(nrd.nr)
        except exc.SQLAlchemyError:
            logging.log(logging.ERROR, 'error in saving NR {0}'.format(nrd))
            return {"message": "An error occurred creating the Name Request."}, 500

        return {"nr": nrd.nr, "message": message}, 201


# noinspection PyUnresolvedReferences
@cors_preflight("GET, PUT, DELETE")
@api.route('/requests/<string:nr>', methods=['GET', 'PUT', 'DELETE', 'OPTIONS'])
class Request(Resource):

    @staticmethod
    @cors.crossdomain(origin='*')
    # @auth_services.requires_auth
    @oidc.accept_token(require_token=True)
    def get(nr):
        # return jsonify(request_schema.dump(RequestDAO.query.filter_by(nr=nr.upper()).first_or_404()))
        return jsonify(RequestDAO.query.filter_by(nr=nr.upper()).first_or_404().json())

    @staticmethod
    @cors.crossdomain(origin='*')
    @oidc.accept_token(require_token=True)
    def delete(nr):
        nrd = RequestDAO.find_by_nr(nr)
        # even if not found we still return a 204, which is expected spec behaviour
        if nrd:
            nrd.status = 'CANCELLED'
            nrd.save_to_db()

        return '', 204

    @staticmethod
    @cors.crossdomain(origin='*')
    @oidc.accept_token(require_token=True)
    def put(nr):
        nrd = RequestDAO.find_by_nr(nr)
        pass

        return '', 501
