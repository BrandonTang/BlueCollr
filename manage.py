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

    default_password = 'Password1'

    # Create 4 users
    user1 = User(email='sahir.karani@gmail.com',
                password=default_password,
                first_name='Sahir',
                last_name='Karani',
                picture_path="/static/img/userpics/default_pic.png",
                validated=True)

    user2 = User(email='matthew.laikhram@gmail.com',
                 password=default_password,
                 first_name='Matthew',
                 last_name='Laikhram',
                 picture_path="/static/img/userpics/default_pic.png",
                 validated=True)

    user3 = User(email='brandon.tang@gmail.com',
                 password=default_password,
                 first_name='Brandon',
                 last_name='Tang',
                 picture_path="/static/img/userpics/default_pic.png",
                 validated=True)

    user4 = User(email='vincent.wong@gmail.com',
                 password=default_password,
                 first_name='Vincent',
                 last_name='Wong',
                 picture_path="/static/img/userpics/default_pic.png",
                 validated=True)

    try:
        # add users
        db.session.add(user1)
        db.session.add(user2)
        db.session.add(user3)
        db.session.add(user4)

        db.session.commit()

        # notify
        print("Added users")

    except Exception as e:

        # error notify
        print("Error adding users")
        print("Error: %s" % e)

    gmaps = googlemaps.Client(key=app.config['MAPS_API'])
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

    try:
        # add jobs
        db.session.add(job1)
        db.session.add(job2)
        db.session.add(job3)
        db.session.add(job4)
        db.session.add(job5)
        db.session.add(job6)
        db.session.add(job7)
        db.session.add(job8)
        db.session.add(job9)

        # notify
        print("Added jobs")

    except Exception as e:

        # error notify
        print("Error adding jobs")
        print("Error: %s" % e)

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

    # hard coded jobs for demo
    geocode_result = gmaps.geocode('185 Montague Street' + ", " + str(11201))
    job10 = Job(name='Fix Heating',
               description='I need someone who can fix my heater. It is broken and it is getting cold out',
               price=3945,
               status=status.PENDING,
               location='185 Montague Street',
               longitude=round(geocode_result[0]['geometry']['location']['lng'], 6),
               latitude=round(geocode_result[0]['geometry']['location']['lat'], 6),
               zipcode=11201,
               creator_id=user1.id,
               date_created=datetime.now())

    geocode_result = gmaps.geocode('100 Willoughby St' + ", " + str(11201))
    job11 = Job(name='Redo Sidewalk',
                description='The sidewalk is broken due to some construction going on. I would like someone to fix it '
                            'ASAP, price is negotiable',
                price=3945,
                status=status.ACCEPTED,
                location='100 Willoughby St',
                longitude=round(geocode_result[0]['geometry']['location']['lng'], 6),
                latitude=round(geocode_result[0]['geometry']['location']['lat'], 6),
                zipcode=11201,
                creator_id=user2.id,
                date_created=datetime.now(),
                accepted_id=user1.id,
                date_accepted=datetime.now())

    geocode_result = gmaps.geocode('49 Flatbush Ave Ext' + ", " + str(11201))
    job12 = Job(name='Clean The Roof',
                description='The roof has many leaves and garbage everywhere. I would like you to clean it.',
                price=70,
                status=status.COMPLETED,
                location='49 Flatbush Ave Ext',
                longitude=round(geocode_result[0]['geometry']['location']['lng'], 6),
                latitude=round(geocode_result[0]['geometry']['location']['lat'], 6),
                zipcode=11201,
                creator_id=user3.id,
                date_created=datetime.now(),
                accepted_id=user1.id,
                rating=4,
                review='Cleaned the roof to expectations but arrived late. Overall I would recommend.',
                date_accepted=datetime.now(),
                date_completed=datetime.now())

    geocode_result = gmaps.geocode('240 Jay St' + ", " + str(11201))
    job13 = Job(name='Repaint Walls',
                description='I need someone to repaint the walls of my home. I will provide paint.',
                price=500,
                status=status.COMPLETED,
                location='240 Jay St',
                longitude=round(geocode_result[0]['geometry']['location']['lng'], 6),
                latitude=round(geocode_result[0]['geometry']['location']['lat'], 6),
                zipcode=11201,
                creator_id=user4.id,
                date_created=datetime.now(),
                accepted_id=user1.id,
                rating=5,
                review='Painted everything perfectly and super fast too! 11/10 would recommend.',
                date_accepted=datetime.now(),
                date_completed=datetime.now())

    geocode_result = gmaps.geocode('287 Myrtle Ave' + ", " + str(11205))
    job14 = Job(name='Building Demolition',
                description='Building must be demolished. Licensed personnel only!',
                price=10000,
                status=status.COMPLETED,
                location='287 Myrtle Ave',
                longitude=round(geocode_result[0]['geometry']['location']['lng'], 6),
                latitude=round(geocode_result[0]['geometry']['location']['lat'], 6),
                zipcode=11205,
                creator_id=user3.id,
                date_created=datetime.now(),
                accepted_id=user2.id,
                rating=1,
                review='Did a bad job, the building next door fell too.',
                date_accepted=datetime.now(),
                date_completed=datetime.now())

    geocode_result = gmaps.geocode('29 Fort Greene Pl' + ", " + str(11217))
    job15 = Job(name='Boiler Replacement',
                description='The boiler must be replaced, the old one keeps breaking down.',
                price=1500,
                status=status.ACCEPTED,
                location='29 Fort Greene Pl',
                longitude=round(geocode_result[0]['geometry']['location']['lng'], 6),
                latitude=round(geocode_result[0]['geometry']['location']['lat'], 6),
                zipcode=11217,
                creator_id=user3.id,
                date_created=datetime.now(),
                accepted_id=user4.id,
                date_accepted=datetime.now())

    geocode_result = gmaps.geocode('336 State St' + ", " + str(11217))
    job16 = Job(name='Hang Photo',
                description='Need a handy person to hang up a photo. Bring a drill please!',
                price=10,
                status=status.PENDING,
                location='185 Montague Street',
                longitude=round(geocode_result[0]['geometry']['location']['lng'], 6),
                latitude=round(geocode_result[0]['geometry']['location']['lat'], 6),
                zipcode=11217,
                creator_id=user2.id,
                date_created=datetime.now())

    try:
        # add jobs
        db.session.add(job10)
        db.session.add(job11)
        db.session.add(job12)
        db.session.add(job13)
        db.session.add(job14)
        db.session.add(job15)
        db.session.add(job16)

        db.session.commit()

        # notify
        print("Added hard coded jobs")

    except Exception as e:

        # error notify
        print("Error adding hard coded jobs")
        print("Error: %s" % e)


if __name__ == '__main__':
    manager.run()
