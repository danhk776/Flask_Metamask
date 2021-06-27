from appli import db


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(100), unique=True)
    token = db.relationship('Token', backref='user')

    def __init__(self, address):
        self.address = address


class Token(db.Model):
    __tablename__ = "token"

    id = db.Column(db.Integer, primary_key=True)
    contract = db.Column(db.String)
    network = db.Column(db.String)
    record = db.Column(db.JSON)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

