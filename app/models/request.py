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
    status = db.Column(db.String(40), default='NEW')
    staff = db.Column(db.String(40), default='UNASSIGNED')
    names = db.relationship('Name', lazy='dynamic')

    STATUS_NEW = 'NEW'
    STATUS_INPROGRESS ='INPROGRESS'
    STATUS_CANCELLED = 'CANCELLED'


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
                'staff': self.staff,
                'status': self.status,
                'names': [name.json() for name in self.names.all()]}

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

    @classmethod
    def get_queued_oldest(cls, userid):
        """Gets the Next NR# from the database
           It sets the STATUS == INPROGRESS
           and then returns the NR or
           error out with a SQLAlchemy Error type
        """
        existing_nr = db.session.query(Request).\
            filter(Request.staff == userid, Request.status == Request.STATUS_INPROGRESS).\
            order_by(Request.timestamp.asc()).\
            first()

        if existing_nr:
            return existing_nr.nr

        r = db.session.query(Request).\
                filter(~Request.status.in_(['CANCELLED', 'INPROGRESS'])).\
                order_by(Request.timestamp.asc()).\
                with_for_update().first()
        # this row is now locked

        r.status= Request.STATUS_INPROGRESS
        r.staff=userid

        db.session.add(r)
        db.session.commit()
        # db.session.close()
        return r.nr


class RequestsSchema(Schema):
    id = fields.Int(dump_only=True)
    nr = fields.String(dump_only=True)
    submitter = fields.String()
    status = fields.String()
    staff = fields.String()
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
