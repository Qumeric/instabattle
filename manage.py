#!/usr/bin/env python
import os
COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()

from subprocess import call
from app import create_app, db
from app.models import User, Role, Image, Permission, Battle, Vote
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
from whitenoise import WhiteNoise

app = create_app(os.environ.get('FLASK_CONFIG'))
manager = Manager(app)
migrate = Migrate(app, db)
# Does it works?!
app = WhiteNoise(app, root='app/static')


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
def test(name=None, coverage=False):
    """Run the unit tests."""
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import sys
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    import unittest
    loader = unittest.TestLoader()
    if name:
        loader.testMethodPrefix = 'test_' + name
    tests = loader.discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()


@manager.command
def init():
    """
    [Re]cretate database, deploy and create three sample users, an image
    and some battles
    """
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


@manager.command
def profile(length=25, profile_dir=None):
    """Start the application under the code profiler."""
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app,
                                      restrictions=[length],
                                      profile_dir=profile_dir)
    app.run()


if __name__ == '__main__':
    manager.run()
