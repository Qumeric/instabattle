#!/usr/bin/env python
import os
from app import create_app, db
from app.models import User, Role, Image, Permission, Battle
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
from flask_moment import Moment

app = create_app(os.environ.get('FLASK_CONFIG'))
manager = Manager(app)
moment = Moment(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app,
                db=db,
                User=User,
                Role=Role,
                Image=Image,
                Permission=Permission,
                Battle=Battle)


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command("db", MigrateCommand)


@manager.command
def test():
    """Tun the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

@manager.command
def deploy():
    from flask_migrate import upgrade

    upgrade()

    Role.insert_roles()

if __name__ == '__main__':
    manager.run()
