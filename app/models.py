from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    psw_hash = db.Column(db.String(128))
    ads = db.relationship('Ad', backref='author', lazy='dynamic')

    #Set password
    def set_password(self, psw):
        self.psw_hash = generate_password_hash(psw)

    #Comprova que el hash del psw sigui igual que psw_hash
    def check_password(self, psw):
        return check_password_hash(self.psw_hash, psw)

    def __repr__(self):
        return '<User {}>'.format(self.username)

class Ad(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), index=True)
    description = db.Column(db.String(1024), index=True)
    category = db.Column(db.String(32), index=True)
    price = db.Column(db.DECIMAL, index=True)
    timestamp = db.Column(db.DateTime, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    images = db.relationship('Image', backref='from_ad', lazy='dynamic', passive_deletes=True)

    def __repr__(self):
        return '<Ad {}>'.format(self.title)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_filename = db.Column(db.String)
    image_url = db.Column(db.String)
    ad_id = db.Column(db.Integer, db.ForeignKey('ad.id', ondelete='CASCADE'))

    def __repr__(self):
        return '<Image {}>'.format(self.link)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))