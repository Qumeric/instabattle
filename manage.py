#!/usr/bin/env python
import os
from subprocess import call
from app import create_app, db
from app.models import User, Role, Image, Permission, Battle, Vote
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
from flask_moment import Moment

app = create_app(os.environ.get('FLASK_CONFIG'))
manager = Manager(app)
moment = Moment(app)
migrate = Migrate(app, db)


def make_shell_context():
    from app.schemas import UserSchema, BattleSchema, ImageSchema, VoteSchema
    return dict(app=app,
                db=db,
                Vote=Vote,
                User=User,
                Role=Role,
                Image=Image,
                Permission=Permission,
                Battle=Battle,
                US=UserSchema(),
                IS=ImageSchema(),
                VS=VoteSchema(),
                BS=BattleSchema())


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command("db", MigrateCommand)


@manager.command
def test(name=None):
    """Run the unit tests."""
    import unittest
    loader = unittest.TestLoader()
    if name:
        loader.testMethodPrefix = 'test_' + name
    tests = loader.discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


@manager.command
def init():
    """[Re]cretate database, deploy and create two sample users and an image"""
    from flask_migrate import init, migrate

    call(["rm", "-rf", "data-dev.sqlite", "migrations"])

    init()
    migrate()
    deploy()

    user_a = User(username='a',
                  email='aa@aa.aa',
                  password='123',
                  confirmed=True)
    user_b = User(username='b',
                  email='bb@bb.bb',
                  password='123',
                  confirmed=True)
    user_c = User(username='c',
                  email='cc@cc.cc',
                  password='123',
                  confirmed=True)
    lenna = Image(name='lenna', user=user_a)
    battle1 = user_a.challenge(user_b, lenna)
    battle1.challenge_accepted = True
    user_c.vote(battle1, "challenger")
    battle2 = user_a.challenge(user_b, lenna)
    battle3 = user_c.challenge(user_a, lenna)

    db.session.add(user_a)
    db.session.add(user_b)
    db.session.add(user_c)
    db.session.add(lenna)
    db.session.add(battle1)
    db.session.add(battle2)
    db.session.add(battle3)
    db.session.commit()


@manager.command
def deploy():
    from flask_migrate import upgrade

    upgrade()

    Role.insert_roles()


if __name__ == '__main__':
    manager.run()
