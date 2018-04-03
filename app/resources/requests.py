from flask import request, jsonify
from flask_restplus import Resource, fields
from marshmallow import ValidationError
from app import api
from sqlalchemy import exc
import logging
from app.models.request import Request as RequestDAO, RequestsSchema


request_schema = RequestsSchema(many=False)
request_schemas = RequestsSchema(many=True)


# noinspection PyUnresolvedReferences,PyPep8
@api.route('/requests/queues/<string:queueName>/oldest', methods=['GET'])
class RequestsNextQueue(Resource):

    # noinspection PyPep8Naming,PyUnusedLocal,PyUnusedLocal
    @staticmethod
    def get(queueName, *args, **kwargs):
        return request_schema.dump(RequestDAO.query.
                                  filter_by(status=queueName.upper()).
                                  order_by(RequestDAO.timestamp.asc()).
                                  first_or_404())


# noinspection PyUnresolvedReferences
@api.route('/requests/queues/<string:queueName>', methods=['GET'])
class RequestsQueues(Resource):

    # noinspection PyPep8Naming,PyUnusedLocal,PyUnusedLocal,PyPep8
    @staticmethod
    def get(queueName, *args, **kwargs):
        # noinspection PyPep8
        return request_schemas.dump(RequestDAO.query.
                                   filter_by(status=queueName.upper()).
                                   order_by(RequestDAO.timestamp.asc()).
                                   all())


@api.route('/requests/queues', methods=['GET'])
class RequestsQueue(Resource):

    # noinspection PyUnusedLocal,PyUnusedLocal
    @staticmethod
    def get(*args, **kwargs):
        # return  request_schema.dump(RequestDAO.query.order_by('timestamp desc').first_or_404())
        return request_schemas.dump(RequestDAO.query.
                                    order_by(RequestDAO.status.asc(),
                                             RequestDAO.timestamp.asc()).all())


@api.route('/requests/queues/oldest', methods=['GET'])
class RequestsQueue(Resource):

    # noinspection PyUnusedLocal,PyUnusedLocal
    @staticmethod
    def get(*args, **kwargs):
        return request_schema.dump(RequestDAO.query.order_by(RequestDAO.timestamp.asc()).first_or_404())


@api.route('/requests', methods=['GET', 'POST'])
class Requests(Resource):
    a_request = api.model('Request', {'submitter': fields.String('The submitter name'),
                                      'corpType': fields.String('The corporation type'),
                                      'reqType': fields.String('The name request type')
                                      })

    # noinspection PyUnusedLocal,PyUnusedLocal
    @staticmethod
    def get(*args, **kwargs):
        # return {'NameRequests': list(map(lambda x: x.json(), RequestsDAO.query.all()))}, 200
        return request_schemas.dump(RequestDAO.query.order_by(RequestDAO.timestamp.asc()).all())

    # noinspection PyUnusedLocal,PyUnusedLocal
    @api.expect(a_request)
    def post(self, *args, **kwargs):

        json_input = request.get_json()
        if not json_input:
            return {'message': 'No input data provided'}, 400

        try:
            data = request_schema.load(json_input)
        except ValidationError as err:
            return jsonify({'errors': err.messages}), 422

        # if RequestDAO.find_by_nr(data[0].nr):
        #      return {'message': "A Name Request '{}' already exists.".format(data[0].nr)}, 400

        nrd = RequestDAO(submitter=data[0].submitter, corpType=data[0].corpType, reqType=data[0].reqType)

        try:
            nrd.save_to_db()
            message = 'Successfully created Name Request: {0}'.format(nrd.nr)
        except exc.SQLAlchemyError:
            logging.log(logging.ERROR, 'error in saving NR {0}'.format(nrd))
            return {"message": "An error occurred creating the Name Request."}, 500

        return {"nr": nrd.nr, "message": message}, 201


# noinspection PyUnresolvedReferences
@api.route('/requests/<string:nr>', methods=['GET', 'DELETE'])
class Request(Resource):

    @staticmethod
    def get(nr):
        return request_schema.dump(RequestDAO.query.filter_by(nr=nr.upper()).first_or_404())

    @staticmethod
    def delete(nr):
        nrd = RequestDAO.find_by_nr(nr)
        if nrd:
            nrd.status = 'CANCELLED'
            nrd.save_to_db()

        return {'message': 'Name Request cancelled'}, 204
