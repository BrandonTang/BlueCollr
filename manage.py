import os
from app import create_app, db
# from app.models import User
from flask import Flask
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
from flask_sqlalchemy import SQLAlchemy
from flask_googlemaps import GoogleMaps
from app.constants import status

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['GOOGLEMAPS_KEY'] = os.environ['GOOGLEMAPS_KEY']
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg'])
app.config['UPLOAD_FOLDER'] = './app/static/img/userpics/'
db = SQLAlchemy(app)

GoogleMaps(app)

with app.app_context():
    from app.models import *

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
def fixdb():
    """fixes spelling errors in the db from before constants was implemented"""
    jobs = Job.query.all()
    for job in jobs:
        job.status = status.PENDING
        job.price = 3.50
        job.review = None
        job.rating = None
        job.accepted_id = None
        job.date_accepted = None
        job.date_completed = None

    users = User.query.all()
    for user in users:
        user.picture_path = "/static/img/userpics/default_pic.png"

    job_requestors = JobRequestor.query.all()
    for job_requestor in job_requestors:
        job_requestor.price = 3.48

    db.session.commit()


@manager.command
def emptydb():
    """deletes all entries in the database"""

    try:
        # clear all requestors
        jobRequestors = JobRequestor.query.all()
        for jobRequestor in jobRequestors:
            db.session.delete(jobRequestor)

        # clear all jobs
        jobs = Job.query.all()
        for job in jobs:
            db.session.delete(job)

        # clear all users
        users = User.query.all()
        for user in users:
            db.session.delete(user)

        # save and inform
        db.session.commit()
        print("Database tables cleared -- success")

    except Exception as e:

        # error notify
        print("Database tables cleared -- failed")
        print("Error: %s" % e)


if __name__ == '__main__':
    manager.run()
