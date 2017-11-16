from app import db
from app.models import Job, JobRequestor, User
from ..jobs import jobs
from ..jobs.forms import CreateJobForm, ReviewJobForm, ZipFilterForm

import operator
import googlemaps
from geopy.distance import vincenty
import datetime
from flask import render_template, current_app, redirect, url_for, flash
from flask_login import login_required, current_user


@jobs.route('/job/<int:id>', methods=['GET', 'POST'])
@login_required
def job(id):
    chosen_job = Job.query.filter_by(id=id).first()
    if chosen_job.creator_id == current_user.id:
        job_requests = JobRequestor.query.filter_by(job_id=id).all()
        requestors = []
        for query in job_requests:
            requestor = User.query.filter_by(id=query.requestor_id).first()
            requestors.append(requestor)

        return render_template('jobs/job.html', job=chosen_job, requestors=requestors)

    return render_template('jobs/job.html', job=chosen_job)


@jobs.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = CreateJobForm()
    if form.validate_on_submit():
        gmaps = googlemaps.Client(key=current_app.config['MAPS_API'])
        geocode_result = gmaps.geocode(form.street_name.data + ", " + str(form.zip_code.data))
        # print round(geocode_result[0]['geometry']['location']['lat'], 6)
        # print round(geocode_result[0]['geometry']['location']['lng'], 6)
        if geocode_result:
            job = Job(name=form.name.data,
                      description=form.description.data,
                      status="Pending",
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
        requested_jobs.append(Job.query.filter_by(id=job_id.job_id).all()[0])
    other_jobs = list(set(Job.query.all()) - set(requested_jobs))
    form = ZipFilterForm()
    if form.validate_on_submit():
        gmaps = googlemaps.Client(key=current_app.config['MAPS_API'])
        geocode_result = gmaps.geocode("Zip Code:" + str(form.zip_code.data))
        if geocode_result:
            location = (round(geocode_result[0]['geometry']['location']['lat'], 6), round(geocode_result[0]['geometry']['location']['lng'], 6))
            distances = {}
            for job in other_jobs:
                job_location = (job.latitude, job.longitude)
                distances[job] = float("{0:.1f}".format(vincenty(location, job_location).miles))
            other_jobs_by_distance = sorted(distances.items(), key=operator.itemgetter(1))
            return render_template('jobs/browse.html', other_sorted=other_jobs_by_distance, requested=requested_jobs, form=form)
        flash('Invalid Zip Code! Please enter a valid Zip Code.', category='success')
        return render_template('jobs/browse.html', other=other_jobs, requested=requested_jobs, form=form)
    return render_template('jobs/browse.html', other=other_jobs, requested=requested_jobs, form=form)


@jobs.route('/my_jobs', methods=['GET', 'POST'])
@login_required
def my_jobs():
    job_list = Job.query.filter_by(creator_id=current_user.id).all()
    request_counts = []
    for job in job_list:
        request_count = JobRequestor.query.filter_by(job_id=job.id).all()
        request_counts.append(len(request_count))

    jobs = dict(zip(job_list, request_counts))
    # worker_list = {}
    # for job in job_list:
    #     current_job = job.id
    #     worker_info = []
    #     worker_ids = JobRequestor.query.filter_by(job_id=current_job).all()
    #     for worker in worker_ids:
    #         worker_name = User.query.filter_by(id=worker.requestor_id).all()[0]
    #         worker_info.append({"worker_id": worker.requestor_id,
    #                             "worker_name": worker_name.first_name + ' ' + worker_name.last_name,
    #                             "job_id": worker.job_id})
    #     worker_list[job] = worker_info
    # print worker_list
    return render_template('jobs/my_jobs.html', jobs=jobs)


@jobs.route('/request/<int:job_id>/<int:requestor_id>', methods=['GET', 'POST'])
@login_required
def request(job_id, requestor_id):
    job_request = JobRequestor(requestor_id=requestor_id, job_id=job_id)
    db.session.add(job_request)
    db.session.commit()
    return redirect(url_for('jobs.browse'))


@jobs.route('/accept/<int:job_id>/<int:requestor_id>', methods=['GET', 'POST'])
@login_required
def accept(job_id, requestor_id):
    accepting_job = Job.query.filter_by(job_id=job_id).first()
    accepting_job.accepted_id = requestor_id
    db.session.commit()
    return redirect(url_for('jobs.my_jobs'))


@jobs.route('/review/<int:id>', methods=['GET', 'POST'])
@login_required
def review(id):
    current_job = Job.query.filter_by(id=id).all()
    form = ReviewJobForm()
    return render_template('jobs/review.html', job=current_job, form=form)
