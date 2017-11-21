from app import db
from ..main import main
from app.models import Job
from ..constants import status

from flask import render_template
from flask_googlemaps import Map


@main.route('/')
def index():
    markers_list = [{
        'icon': '/static/img/icons/hq.png',
        'lat': 40.6939904,
        'lng': -73.98656399999999,
        'infobox': "BlueCollr HQ"
    }]

    jobs = Job.query.all()

    for job in jobs:
        name = job.name
        description = job.description
        price = job.price
        link = "/jobs/job/" + str(job.id)
        latitude = job.latitude
        longitude = job.longitude
        if job.status == status.PENDING:
            icon = '/static/img/icons/open.png'
        elif job.status == status.ACCEPTED:
            icon = '/static/img/icons/accepted.png'
        else:
            icon = '/static/img/icons/completed.png'
        markers_list.append({'icon': icon,
                             'lat': latitude,
                             'lng': longitude,
                             'infobox': ("<center>Job Name: " + name +
                                         "<br/>Description: " + description +
                                         "<br/>Job Status: " + job.status +
                                         "<br/>Price: $" + "{0:.2f}".format(price) +
                                         "<br/><a href = '" + link + "' > View </a> ")
                             })

    bluecollr_jobs_map = Map(
        identifier="bluecollr_map",
        zoom=15,
        lat=40.6939904,
        lng=-73.98656399999999,
        markers=markers_list,
        scroll_wheel=False,
        style="height:80vh;width:100%;margin:3% 0%;"
    )
    return render_template('index.html', bluecollr_jobs_map=bluecollr_jobs_map)
