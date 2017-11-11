import os
from app import create_app, db
# from app.models import User
from flask import Flask
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
from flask_sqlalchemy import SQLAlchemy
from app.models import User

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
# db = SQLAlchemy(app)
manager = Manager(app)
migrate = Migrate(app, db)

def make_shell_context():
    return dict(app=app, db=db, User=User)

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


@manager.command
def testing():
    """for testing purposes"""
    print(os.environ.get('POSTGRESQL_CONNECTION'))
    print("postgresql://bluecollr:password@localhost/bluecollr")
    print(os.environ.get('POSTGRESQL_CONNECTION') == "postgresql://bluecollr:password@localhost/bluecollr")


if __name__ == '__main__':
    manager.run()