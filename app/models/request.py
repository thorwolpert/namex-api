from app import db
from sqlalchemy import Sequence
from marshmallow import Schema, fields, post_load
from datetime import datetime


# create sequence if not exists nr_seq;
# noinspection PyPep8Naming
class Request(db.Model):
    __tablename__ = 'requests'

    id = db.Column(db.Integer, primary_key=True)
    nr = db.Column(db.String(10), unique=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    submitter = db.Column(db.String(80))
    corpType = db.Column('corptype', db.String(80))
    reqType = db.Column('reqtype', db.String(80))
    status = db.Column(db.String(20), default='NEW')

    # names = db.relationship('NameDAO', lazy='dynamic')

    def __init__(self, submitter, corpType, reqType):
        self.submitter = submitter
        self.corpType = corpType
        self.reqType = reqType

    def json(self):
        return {'nr': self.nr,
                'corpType': self.corpType,
                'reqType': self.reqType,
                'submitter': self.submitter,
                'timestamp': self.timestamp.isoformat(),
                'status': self.status}
        # 'names': [name.json() for name in self.names.all()]

    @classmethod
    def find_by_nr(cls, nr):
        return cls.query.filter_by(nr=nr).first()

    def save_to_db(self):
        if self.id is None:
            # NR is not the primary key, but has to be a unique value.
            seq = Sequence('nr_seq')
            next_nr = db.engine.execute(seq)
            self.nr = 'NR{0:0>8}'.format(next_nr)

        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()


class RequestsSchema(Schema):
    id = fields.Int(dump_only=True)
    nr = fields.String(dump_only=True)
    submitter = fields.String()
    status = fields.String()
    corpType = fields.String()
    reqType = fields.String()

    # We use make_object to create a new Request from validated data
    @post_load
    def make_object(self, data):
        if not data:
            return None
        return Request(submitter=data['submitter'],
                       corpType=data['corpType'],
                       reqType=data['reqType'])
