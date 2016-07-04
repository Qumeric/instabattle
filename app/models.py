from datetime import datetime
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request
from . import db, login_manager


class Permission:
    CHALLENGE = 0x01
    VOTE = 0x02
    SUGGEST = 0x04
    APPROVE = 0x08
    ADMINISTER = 0x80


class Role(db.Model):  # FIXME do I need it?
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = (('User', Permission.CHALLENGE | Permission.VOTE |
                  Permission.SUGGEST, True),
                 ('Moderator', Permission.CHALLENGE | Permission.SUGGEST |
                  Permission.APPROVE, False), ('Administrator', 0xff, False))
        for name, permissions, default in roles:
            role = Role.query.filter_by(name=name).first()
            if role is None:
                role = Role(name=name)
            role.permissions = permissions
            role.default = default
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return "<Role {}>".format(self.name)

class Vote(db.Model):
    __tablename__ = 'votes'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    battle_id = db.Column(db.Integer, db.ForeignKey('battles.id'), primary_key=True)
    choice = db.Column(db.Enum('challenger', 'challenged'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

class Battle(db.Model):
    __tablename__ = 'battles'
    id = db.Column(db.Integer, primary_key=True)
    challenger_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    challenged_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    image_id = db.Column(db.Integer, db.ForeignKey('images.id'))
    challenge_accepted = db.Column(db.Boolean, default=False)
    challenger_finished = db.Column(db.Boolean, default=False)
    challenged_finished = db.Column(db.Boolean, default=False)
    is_finished = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    votes = db.relationship(
        'Vote',
        backref='battle',
        lazy='dynamic',
        cascade='all, delete-orphan')

    def __repr__(self):
        return "<Battle between {} and {}>".format(
            User.query.filter_by(id=self.challenger_id).first().username,
            User.query.filter_by(id=self.challenged_id).first().username)


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    name = db.Column(db.String(64))
    email = db.Column(db.String(120), unique=True, index=True)
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    images = db.relationship('Image', backref='user', lazy='dynamic')
    challenged_by = db.relationship(
        'Battle',
        foreign_keys=[Battle.challenged_id],
        backref=db.backref('challenged', lazy='joined'), # FIXME why lazy='joined'?
        lazy='dynamic',
        cascade='all, delete-orphan')
    challenged_who = db.relationship(
        'Battle',
        foreign_keys=[Battle.challenger_id],
        backref=db.backref('challenger', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan')
    votes = db.relationship(
        'Vote',
        backref='voter',
        lazy='dynamic',
        cascade='all, delete-orphan')

    

    avatar_hash = db.Column(db.String(32))

    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                     username=forgery_py.internet.user_name(True),
                     password=forgery_py.lorem_ipsum.word(),
                     confirmed=True,
                     name=forgery_py.name.full_name(),
                     about_me=forgery_py.lorem_ipsum.sentence(),
                     member_since=forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(self.email.encode()).hexdigest()

    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_reset_token(self, expiration=60 * 60):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        db.session.commit()
        return True

    def generate_confirmation_token(self, expiration=60 * 60):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        db.session.commit()
        return True

    def challenge(self, user, image):
        if self.id == user.id:
            raise ValueError("A user cannot challenge himself")
        battle = Battle(challenger=self, # FIXME check
                        challenged=user,
                        image=image)
        db.session.add(battle)
        db.session.commit()
        return battle

    def can(self, permissions):
        return self.role and (self.role.permissions & permissions
                              ) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def gravatar(self, size=100, default='identicon', rating='pg'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(self.email.encode()).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url,
            hash=hash,
            size=size,
            default=default,
            rating=rating)

    @property
    def battles(self):
        return self.challenged_by.union(self.challenged_who).order_by(Battle.timestamp.desc())

    def __repr__(self):
        return "<User {}>".format(self.email)


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Image(db.Model):
    __tablename__ = 'images'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    battles = db.relationship('Battle', backref='image', lazy='dynamic')

    def __repr__(self):
        return "<Image {}>".format(self.name)

