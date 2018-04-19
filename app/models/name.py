from app import db

class Name(db.Model):
    __tablename__ = 'names'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1024))
    status = db.Column(db.String(40), default='NEW')
    choice = db.Column(db.Integer)

    nr_id = db.Column(db.Integer, db.ForeignKey('requests.id'))
    nameRequest = db.relationship('Request')

    def __init__(self, name, choice, nr_id):
        self.name = name
        self.choice = choice
        self.nr_id = nr_id

    def json(self):
        return {'name': self.name, 'choice': self.choice, 'stats': self.status}

    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
