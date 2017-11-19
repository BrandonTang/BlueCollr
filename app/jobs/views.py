from app import db
from app.models import Job, JobRequestor, User
from ..jobs import jobs
from ..jobs.forms import CreateJobForm, ReviewJobForm, ZipFilterForm, PriceForm
from ..constants import status

import operator
import googlemaps
import datetime
from geopy.distance import vincenty
from flask import render_template, current_app, redirect, url_for, flash
from flask_login import login_required, current_user
from flask_googlemaps import Map


@jobs.route('/job/<int:id>', methods=['GET', 'POST'])
@login_required
def job(id):
    chosen_job = Job.query.filter_by(id=id).first()
    if chosen_job.status == status.PENDING and chosen_job.creator_id == current_user.id:
        job_requests = JobRequestor.query.filter_by(job_id=id).all()
        requestors = {}
        for query in job_requests:
            requestor = User.query.filter_by(id=query.requestor_id).first()
            requestors[requestor] = query.price

        return render_template('jobs/job.html', job=chosen_job, requestors=requestors)

    elif chosen_job.status == status.PENDING:
        price_form = PriceForm()

        if price_form.validate_on_submit():
            job_request = JobRequestor(requestor_id=current_user.id,
                                       job_id=id,
                                       price=price_form.price.data)
            db.session.add(job_request)
            db.session.commit()
            flash('Request has been sent!', category='success')
            return render_template('jobs/job.html', job=chosen_job)

        job_request = JobRequestor.query.filter_by(job_id=id, requestor_id=current_user.id).first()
        if job_request is not None:
            return render_template('jobs/job.html', job=chosen_job)

        price_form.price.data = chosen_job.price

        return render_template('jobs/job.html', job=chosen_job, form=price_form)

    elif chosen_job.status != status.PENDING:
        acceptor = User.query.filter_by(id=chosen_job.accepted_id).first()

        return render_template('jobs/job.html', job=chosen_job, acceptor=acceptor)

    return render_template('jobs/job.html', job=chosen_job)


@jobs.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = CreateJobForm()
    if form.validate_on_submit():
        gmaps = googlemaps.Client(key=current_app.config['MAPS_API'])
        geocode_result = gmaps.geocode(form.street_name.data + ", " + str(form.zip_code.data))
        if geocode_result:
            job = Job(name=form.name.data,
                      description=form.description.data,
                      price=form.price.data,
                      status=status.PENDING,
                      location=form.street_name.data,
                      longitude=round(geocode_result[0]['geometry']['location']['lng'], 6),
                      latitude=round(geocode_result[0]['geometry']['location']['lat'], 6),
                      zipcode=form.zip_code.data,
                      creator_id=current_user.id,
                      date_created=datetime.datetime.now())
            db.session.add(job)
            db.session.commit()
            flash('Job successfully created!', category='success')
            return redirect(url_for('jobs.browse'))
        flash('Invalid Address! Please enter a valid address.', category='success')
        return redirect(url_for('jobs.create'))
    return render_template('jobs/create.html', form=form)


@jobs.route('/browse', methods=['GET', 'POST'])
@login_required
def browse():
    requested_jobs = []
    requested_ids = JobRequestor.query.filter_by(requestor_id=current_user.id).all()
    for job_id in requested_ids:
        requested_job = Job.query.filter_by(id=job_id.job_id, status=status.PENDING).first()
        if requested_job is not None:
            requested_jobs.append(requested_job)
    my_own_jobs = Job.query.filter_by(creator_id=current_user.id).all()
    other_jobs = list(set(Job.query.filter_by(status=status.PENDING).all()) - set(requested_jobs) - set(my_own_jobs))
    form = ZipFilterForm()
    markers_list = [{
        'icon': 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png',
        'lat': 40.6939904,
        'lng': -73.98656399999999,
        'infobox': "BlueCollr HQ"
    }]

    for job in other_jobs:
        name = job.name
        description = job.description
        price = job.price
        link = "/jobs/job/" + str(job.id)
        latitude = job.latitude
        longitude = job.longitude
        markers_list.append({'icon': 'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
                             'lat': latitude,
                             'lng': longitude,
                             'infobox': ("Job Name: " + name +
                                         "<br/>Description: " + description +
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
        style="height:50vh;width:100%;margin:3% 0%;"
    )
    if form.validate_on_submit():
        gmaps = googlemaps.Client(key=current_app.config['MAPS_API'])
        geocode_result = gmaps.geocode("Zip Code:" + str(form.zip_code.data))
        if geocode_result:
            location = (round(geocode_result[0]['geometry']['location']['lat'], 6),
                        round(geocode_result[0]['geometry']['location']['lng'], 6))
            markers_list.append({
                'icon': 'http://maps.google.com/mapfiles/ms/icons/red-dot.png',
                'lat': round(geocode_result[0]['geometry']['location']['lat'], 6),
                'lng': round(geocode_result[0]['geometry']['location']['lng'], 6),
                'infobox': "Current Location"
            })
            bluecollr_jobs_map = Map(
                identifier="bluecollr_map",
                zoom=15,
                lat=geocode_result[0]['geometry']['location']['lat'],
                lng=geocode_result[0]['geometry']['location']['lng'],
                markers=markers_list,
                scroll_wheel=False,
                style="height:50vh;width:100%;margin:3% 0%;"
            )
            distances = {}
            for job in other_jobs:
                job_location = (job.latitude, job.longitude)
                distances[job] = float("{0:.1f}".format(vincenty(location, job_location).miles))
            other_jobs_by_distance = sorted(distances.items(), key=operator.itemgetter(1))
            return render_template('jobs/browse.html', bluecollr_jobs_map=bluecollr_jobs_map,
                                   other_sorted=other_jobs_by_distance, form=form)
        flash('Invalid Zip Code! Please enter a valid Zip Code.', category='success')
        return render_template('jobs/browse.html', bluecollr_jobs_map=bluecollr_jobs_map, other=other_jobs, form=form)
    return render_template('jobs/browse.html', bluecollr_jobs_map=bluecollr_jobs_map, other=other_jobs, form=form)


@jobs.route('/my_requests', methods=['GET', 'POST'])
@login_required
def my_requests():
    accepted_jobs = Job.query.filter_by(accepted_id=current_user.id). \
        filter((Job.status == status.ACCEPTED) |
               (Job.status == status.CREATOR_VER) |
               (Job.status == status.WORKER_VER)).all()

    requested_jobs = {}
    requested_ids = JobRequestor.query.filter_by(requestor_id=current_user.id).all()
    for job_id in requested_ids:
        requested_job = Job.query.filter_by(id=job_id.job_id, status=status.PENDING).first()
        if requested_job is not None:
            requested_jobs[requested_job] = job_id.price

    form = ZipFilterForm()
    markers_list = [{
        'icon': 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png',
        'lat': 40.6939904,
        'lng': -73.98656399999999,
        'infobox': "BlueCollr HQ"
    }]

    for job in accepted_jobs:
        name = job.name
        description = job.description
        price = job.price
        link = "/jobs/job/" + str(job.id)
        latitude = job.latitude
        longitude = job.longitude
        markers_list.append({'icon': 'http://maps.google.com/mapfiles/ms/icons/orange-dot.png',
                             'lat': latitude,
                             'lng': longitude,
                             'infobox': ("Job Name: " + name +
                                         "<br/>Description: " + description +
                                         "<br/>Job Status: " + job.status +
                                         "<br/>Price: $" + "{0:.2f}".format(price) +
                                         "<br/><a href = '" + link + "' > View </a> ")
                             })

    for job in requested_jobs:
        name = job.name
        description = job.description
        price = job.price
        link = "/jobs/job/" + str(job.id)
        latitude = job.latitude
        longitude = job.longitude
        markers_list.append({'icon': 'http://maps.google.com/mapfiles/ms/icons/yellow-dot.png',
                             'lat': latitude,
                             'lng': longitude,
                             'infobox': ("Job Name: " + name +
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
        style="height:50vh;width:100%;margin:3% 0%;"
    )
    if form.validate_on_submit():
        gmaps = googlemaps.Client(key=current_app.config['MAPS_API'])
        geocode_result = gmaps.geocode("Zip Code:" + str(form.zip_code.data))
        if geocode_result:
            location = (round(geocode_result[0]['geometry']['location']['lat'], 6),
                        round(geocode_result[0]['geometry']['location']['lng'], 6))
            markers_list.append({
                'icon': 'http://maps.google.com/mapfiles/ms/icons/red-dot.png',
                'lat': round(geocode_result[0]['geometry']['location']['lat'], 6),
                'lng': round(geocode_result[0]['geometry']['location']['lng'], 6),
                'infobox': "Current Location"
            })
            bluecollr_jobs_map = Map(
                identifier="bluecollr_map",
                zoom=15,
                lat=geocode_result[0]['geometry']['location']['lat'],
                lng=geocode_result[0]['geometry']['location']['lng'],
                markers=markers_list,
                scroll_wheel=False,
                style="height:50vh;width:100%;margin:3% 0%;"
            )
            distances_1 = {}
            for job in accepted_jobs:
                job_location = (job.latitude, job.longitude)
                distances_1[job] = float("{0:.1f}".format(vincenty(location, job_location).miles))
            accepted_jobs_by_distance = sorted(distances_1.items(), key=operator.itemgetter(1))

            distances_2 = {}
            for job in requested_jobs:
                job_location = (job.latitude, job.longitude)
                distances_2[job] = float("{0:.1f}".format(vincenty(location, job_location).miles))
            requested_jobs_by_distance = sorted(distances_2.items(), key=operator.itemgetter(1))

            return render_template('jobs/my_requests.html',
                                   bluecollr_jobs_map=bluecollr_jobs_map,
                                   accepted_sorted=accepted_jobs_by_distance,
                                   requested_sorted=requested_jobs_by_distance,
                                   form=form)

        flash('Invalid Zip Code! Please enter a valid Zip Code.', category='success')
        return render_template('jobs/my_requests.html', bluecollr_jobs_map=bluecollr_jobs_map,
                               accepted_jobs=accepted_jobs, requested_jobs=requested_jobs, form=form)

    return render_template('jobs/my_requests.html', bluecollr_jobs_map=bluecollr_jobs_map,
                           accepted_jobs=accepted_jobs, requested_jobs=requested_jobs, form=form)


@jobs.route('/my_jobs', methods=['GET', 'POST'])
@login_required
def my_jobs():
    job_list = Job.query.filter_by(creator_id=current_user.id, status=status.ACCEPTED).all()

    acceptors = []
    for job in job_list:
        acceptor = User.query.filter_by(id=job.accepted_id).first()
        acceptors.append(acceptor)
    accepted_jobs = dict(zip(job_list, acceptors))

    job_list = Job.query.filter_by(creator_id=current_user.id, status=status.PENDING).all()
    request_counts = []
    for job in job_list:
        request_count = JobRequestor.query.filter_by(job_id=job.id).all()
        request_counts.append(len(request_count))
    pending_jobs = dict(zip(job_list, request_counts))

    job_list = Job.query.filter_by(creator_id=current_user.id, status=status.COMPLETED).all()

    acceptors = []
    for job in job_list:
        acceptor = User.query.filter_by(id=job.accepted_id).first()
        acceptors.append(acceptor)
    completed_jobs = dict(zip(job_list, acceptors))

    form = ZipFilterForm()
    markers_list = [{
        'icon': 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png',
        'lat': 40.6939904,
        'lng': -73.98656399999999,
        'infobox': "BlueCollr HQ"
    }]

    for job in accepted_jobs:
        name = job.name
        description = job.description
        price = job.price
        link = "/jobs/job/" + str(job.id)
        latitude = job.latitude
        longitude = job.longitude
        markers_list.append({'icon': 'http://maps.google.com/mapfiles/ms/icons/orange-dot.png',
                             'lat': latitude,
                             'lng': longitude,
                             'infobox': ("Job Name: " + name +
                                         "<br/>Description: " + description +
                                         "<br/>Job Status: " + job.status +
                                         "<br/>Price: $" + "{0:.2f}".format(price) +
                                         "<br/><a href = '" + link + "' > View </a> ")
                             })

    for job in pending_jobs:
        name = job.name
        description = job.description
        price = job.price
        link = "/jobs/job/" + str(job.id)
        latitude = job.latitude
        longitude = job.longitude
        markers_list.append({'icon': 'http://maps.google.com/mapfiles/ms/icons/yellow-dot.png',
                             'lat': latitude,
                             'lng': longitude,
                             'infobox': ("Job Name: " + name +
                                         "<br/>Description: " + description +
                                         "<br/>Job Status: " + job.status +
                                         "<br/>Price: $" + "{0:.2f}".format(price) +
                                         "<br/><a href = '" + link + "' > View </a> ")
                             })

    for job in completed_jobs:
        name = job.name
        description = job.description
        price = job.price
        link = "/jobs/job/" + str(job.id)
        latitude = job.latitude
        longitude = job.longitude
        markers_list.append({'icon': 'http://maps.google.com/mapfiles/ms/icons/yellow-dot.png',
                             'lat': latitude,
                             'lng': longitude,
                             'infobox': ("Job Name: " + name +
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
        style="height:50vh;width:100%;margin:3% 0%;"
    )
    if form.validate_on_submit():
        gmaps = googlemaps.Client(key=current_app.config['MAPS_API'])
        geocode_result = gmaps.geocode("Zip Code:" + str(form.zip_code.data))
        if geocode_result:
            location = (round(geocode_result[0]['geometry']['location']['lat'], 6),
                        round(geocode_result[0]['geometry']['location']['lng'], 6))
            markers_list.append({
                'icon': 'http://maps.google.com/mapfiles/ms/icons/red-dot.png',
                'lat': round(geocode_result[0]['geometry']['location']['lat'], 6),
                'lng': round(geocode_result[0]['geometry']['location']['lng'], 6),
                'infobox': "Current Location"
            })
            bluecollr_jobs_map = Map(
                identifier="bluecollr_map",
                zoom=15,
                lat=geocode_result[0]['geometry']['location']['lat'],
                lng=geocode_result[0]['geometry']['location']['lng'],
                markers=markers_list,
                scroll_wheel=False,
                style="height:50vh;width:100%;margin:3% 0%;"
            )
            distances_1 = {}
            for job in accepted_jobs:
                job_location = (job.latitude, job.longitude)
                distances_1[job] = float("{0:.1f}".format(vincenty(location, job_location).miles))
            accepted_jobs_by_distance = sorted(distances_1.items(), key=operator.itemgetter(1))

            distances_2 = {}
            for job in pending_jobs:
                job_location = (job.latitude, job.longitude)
                distances_2[job] = float("{0:.1f}".format(vincenty(location, job_location).miles))
            pending_jobs_by_distance = sorted(distances_2.items(), key=operator.itemgetter(1))

            distances_3 = {}
            for job in completed_jobs:
                job_location = (job.latitude, job.longitude)
                distances_3[job] = float("{0:.1f}".format(vincenty(location, job_location).miles))
            completed_jobs_by_distance = sorted(distances_3.items(), key=operator.itemgetter(1))

            return render_template('jobs/my_jobs.html',
                                   form=form,
                                   bluecollr_jobs_map=bluecollr_jobs_map,
                                   accepted_sorted=accepted_jobs_by_distance,
                                   pending_sorted=pending_jobs_by_distance,
                                   completed_sorted=completed_jobs_by_distance)

        flash('Invalid Zip Code! Please enter a valid Zip Code.', category='success')
        return render_template('jobs/my_jobs.html',
                               form=form,
                               bluecollr_jobs_map=bluecollr_jobs_map,
                               accepted_jobs=accepted_jobs,
                               pending_jobs=pending_jobs,
                               completed_jobs=completed_jobs)

    return render_template('jobs/my_jobs.html',
                           form=form,
                           bluecollr_jobs_map=bluecollr_jobs_map,
                           accepted_jobs=accepted_jobs,
                           pending_jobs=pending_jobs,
                           completed_jobs=completed_jobs)



@jobs.route('/accept_request/<int:job_id>/<int:requestor_id>', methods=['GET', 'POST'])
@login_required
def accept_request(job_id, requestor_id):
    job = Job.query.filter_by(id=job_id).first()
    if current_user.id == job.creator_id:
        job.accepted_id = requestor_id
        job.date_accepted = datetime.datetime.now()
        job.status = status.ACCEPTED
        db.session.commit()
        requestor = User.query.filter_by(id=requestor_id).first()
        flash("Request for job successfully accepted!")
        return render_template('jobs/job.html', job=job, acceptor=requestor)
    flash("Please do not try to accept jobs for other people!")
    return url_for('jobs/job.html', job=job)


@jobs.route('/request/<int:job_id>/<int:requestor_id>', methods=['GET', 'POST'])
@login_required
def quick_request(job_id, requestor_id):
    if current_user.id == requestor_id:
        job = Job.query.filter_by(id=job_id).first()
        job_request = JobRequestor(requestor_id=requestor_id,
                                   job_id=job_id,
                                   price=job.price)
        db.session.add(job_request)
        db.session.commit()
        flash("Job successfully quick requested!")
        return redirect(url_for('jobs.browse'))
    flash("Please do not try to sign other people up for jobs!")
    return redirect(url_for('jobs.browse'))


@jobs.route('/review/<int:job_id>', methods=['GET', 'POST'])
@login_required
def review(job_id):
    job = Job.query.filter_by(id=job_id).first()
    form = ReviewJobForm()
    if form.validate_on_submit():
        if current_user.id == job.creator_id:
            job.rating = int(form.rating.data)
            job.review = form.review.data
            job.date_completed = datetime.datetime.now()
            job.status = status.COMPLETED
            db.session.commit()
            flash("Job review sucessfully submitted!")
            return redirect(url_for('jobs.job', id=job_id))
        flash("Please do not try to mark other peoples jobs as complete!")
        return redirect(url_for('jobs.my_jobs'))
    return render_template('jobs/review.html', job=job, form=form)
