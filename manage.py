import os
from app import create_app, db
# from app.models import User
from flask import Flask
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
from flask_sqlalchemy import SQLAlchemy
from flask_googlemaps import GoogleMaps
from app.constants import status
import googlemaps
import datetime
import random

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['GOOGLEMAPS_KEY'] = os.environ['GOOGLEMAPS_KEY']
app.config['MAPS_API'] = os.environ['MAPS_API']
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


@manager.command
def populatedb():
    """fills database with fake 'real' data"""

    default_password = 'Toontown123'

    # Create 4 users
    user1 = User(email='abc@gmail.com',
                password=default_password,
                first_name='Sahir',
                last_name='Karani',
                picture_path="/static/img/userpics/default_pic.png",
                validated=True)
    db.session.add(user1)
    user2 = User(email='def@gmail.com',
                 password=default_password,
                 first_name='Matthew',
                 last_name='Laikhram',
                 picture_path="/static/img/userpics/default_pic.png",
                 validated=True)
    db.session.add(user2)
    user3 = User(email='ghi@gmail.com',
                 password=default_password,
                 first_name='Brandon',
                 last_name='Tang',
                 picture_path="/static/img/userpics/default_pic.png",
                 validated=True)
    db.session.add(user3)
    user4 = User(email='jkl@gmail.com',
                 password=default_password,
                 first_name='Vincent',
                 last_name='Wong',
                 picture_path="/static/img/userpics/default_pic.png",
                 validated=True)
    db.session.add(user4)

    print("Users added")

    # Create jobs
    gmaps = googlemaps.Client(key=app.config['MAPS_API'])
    # User 1
    geocode_result = gmaps.geocode('1600 Pennsylvania Ave' + ", " + str(20500))
    job1 = Job(name='Insulation Replacement',
              description='Need to replace the insulation in my basement',
              price=150,
              status=status.PENDING,
              location='1600 Pennsylvania Ave',
              longitude=round(geocode_result[0]['geometry']['location']['lng'], 6),
              latitude=round(geocode_result[0]['geometry']['location']['lat'], 6),
              zipcode=20500,
              creator_id=user1.id,
              date_created=datetime.now())
    db.session.add(job1)
    geocode_result = gmaps.geocode('11 Wall Street' + ", " + str(10005))
    job2 = Job(name='Bathroom Renovation',
               description='Need to redecorate my upstairs bathroom',
               price=500,
               status=status.PENDING,
               location='11 Wall Street',
               longitude=round(geocode_result[0]['geometry']['location']['lng'], 6),
               latitude=round(geocode_result[0]['geometry']['location']['lat'], 6),
               zipcode=10005,
               creator_id=user1.id,
               date_created=datetime.now())
    db.session.add(job2)
    geocode_result = gmaps.geocode('N 6th St & Market St' + ", " + str(19106))
    job3 = Job(name='Kitchen Sink Leaking',
               description='Need someone to snake my pipes',
               price=150,
               status=status.PENDING,
               location='N 6th St & Market St',
               longitude=round(geocode_result[0]['geometry']['location']['lng'], 6),
               latitude=round(geocode_result[0]['geometry']['location']['lat'], 6),
               zipcode=19106,
               creator_id=user1.id,
               date_created=datetime.now())
    db.session.add(job3)
    # User 2
    geocode_result = gmaps.geocode('50 W 10th St' + ", " + str(10011))
    job4 = Job(name='Raking Leaves',
               description='Need to rake leaves in backyard',
               price=90,
               status=status.PENDING,
               location='50 W 10th St',
               longitude=round(geocode_result[0]['geometry']['location']['lng'], 6),
               latitude=round(geocode_result[0]['geometry']['location']['lat'], 6),
               zipcode=10011,
               creator_id=user2.id,
               date_created=datetime.now())
    db.session.add(job4)
    geocode_result = gmaps.geocode('77 Saint Marks Place' + ", " + str(10003))
    job5 = Job(name='Build a swing set',
               description='Need help building swing set',
               price=500,
               status=status.PENDING,
               location='77 Saint Marks Place',
               longitude=round(geocode_result[0]['geometry']['location']['lng'], 6),
               latitude=round(geocode_result[0]['geometry']['location']['lat'], 6),
               zipcode=10003,
               creator_id=user2.id,
               date_created=datetime.now())
    db.session.add(job5)
    geocode_result = gmaps.geocode('778 Park Avenue' + ", " + str(10021))
    job6 = Job(name='Painting',
               description='Need to paint my walls bright pink',
               price=100,
               status=status.PENDING,
               location='778 Park Avenue',
               longitude=round(geocode_result[0]['geometry']['location']['lng'], 6),
               latitude=round(geocode_result[0]['geometry']['location']['lat'], 6),
               zipcode=10021,
               creator_id=user2.id,
               date_created=datetime.now())
    db.session.add(job6)
    # User 3
    geocode_result = gmaps.geocode('419 West 115th Street' + ", " + str(10025))
    job7 = Job(name='Moving Furniture',
               description='Need help packing furniture onto moving truck',
               price=300,
               status=status.PENDING,
               location='419 West 115th Street',
               longitude=round(geocode_result[0]['geometry']['location']['lng'], 6),
               latitude=round(geocode_result[0]['geometry']['location']['lat'], 6),
               zipcode=10025,
               creator_id=user3.id,
               date_created=datetime.now())
    db.session.add(job7)
    geocode_result = gmaps.geocode('441 East 9th Street' + ", " + str(10009))
    job8 = Job(name='Demolition',
               description='Need to tear down wall',
               price=200,
               status=status.PENDING,
               location='441 East 9th Street',
               longitude=round(geocode_result[0]['geometry']['location']['lng'], 6),
               latitude=round(geocode_result[0]['geometry']['location']['lat'], 6),
               zipcode=10009,
               creator_id=user3.id,
               date_created=datetime.now())
    db.session.add(job8)
    geocode_result = gmaps.geocode('45 West 10th Street' + ", " + str(10011))
    job9 = Job(name='Replacing wood flooring',
               description='Need someone to replace wood flooring',
               price=1000,
               status=status.PENDING,
               location='45 West 10th Street',
               longitude=round(geocode_result[0]['geometry']['location']['lng'], 6),
               latitude=round(geocode_result[0]['geometry']['location']['lat'], 6),
               zipcode=10011,
               creator_id=user3.id,
               date_created=datetime.now())
    db.session.add(job9)

    print("Jobs added")

    # Create job_requestors
    users = User.query.all()
    jobs = Job.query.all()

    for user in users:
        for job in jobs:
            x = random.randint(1,101)
            if x < 50 and user.id != job.creator_id:
                job_request = JobRequestor(requestor_id=user.id,
                                           job_id=job.id,
                                           price=job.price)
                db.session.add(job_request)

    print("Job_requestors added")

    db.session.commit()


if __name__ == '__main__':
    manager.run()
