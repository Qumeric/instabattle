from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import db, login_manager


class Role(db.Model):  # FIXME do I need it?
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return "<Role {}>".format(self.name)


class Battle(db.Model):
    __tablename__ = 'battles'
    id = db.Column(db.Integer, primary_key=True)
    challenger_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    challenged_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    image_id = db.Column(db.Integer, db.ForeignKey('images.id'))
    challenger_finished = db.Column(db.Boolean, default=False)
    challenged_finished = db.Column(db.Boolean, default=False)
    winner = db.Column(
        db.Enum('none', 'challenger', 'challenged'),
        default='none')
    challenger_votes = db.Column(db.Integer, default=0)
    challenged_votes = db.Column(db.Integer, default=0)

    def __repr__(self):
        return "<Battle between {} and {}>".format(
            User.query.filter_by(id=user1_id).email,
            User.query.filter_by(id=user2_id).email)


challenges = db.Table(
    'challenges', db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('battle_id', db.Integer, db.ForeignKey('battles.id')))


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    images = db.relationship('Image', backref='user', lazy='dynamic')
    battles = db.relationship(
        'Battle',
        secondary=challenges,
        backref=db.backref('users', lazy='dynamic'), # FIXME lazy='joined'?
        lazy='dynamic')

    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def challenge(self, user_id, image_id):
        if self.id == user_id:
            raise ValueError("A user cannot challenge himself")
        battle = Battle(challenger_id=self.id, challenged_id=user_id, image_id=image_id)
        db.session.add(battle)
        self.battles.append(battle)
        db.session.commit()
        return battle

    def __repr__(self):
        return "<User {}>".format(self.email)


class Image(db.Model):
    __tablename__ = 'images'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
