from app import db
from app.models import Job, JobRequestor, User
from ..jobs import jobs
from ..jobs.forms import CreateJobForm, ReviewJobForm

import googlemaps
import datetime
from flask import render_template, current_app, redirect, url_for, flash
from flask_login import login_required, current_user


@jobs.route('/job/<int:id>', methods=['GET', 'POST'])
@login_required
def job(id):
    chosen_job = Job.query.filter_by(id=id).all()[0]
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
    return render_template('jobs/browse.html', other=other_jobs, requested=requested_jobs)


@jobs.route('/my_jobs', methods=['GET', 'POST'])
@login_required
def my_jobs():
    job_list = Job.query.filter_by(creator_id=current_user.id).all()
    worker_list = {}
    for job in job_list:
        current_job = job.id
        worker_info = []
        worker_ids = JobRequestor.query.filter_by(job_id=current_job).all()
        for worker in worker_ids:
            worker_name = User.query.filter_by(id=worker.requestor_id).all()[0]
            worker_info.append({"worker_id": worker.requestor_id,
                                "worker_name": worker_name.first_name + ' ' + worker_name.last_name,
                                "job_id": worker.job_id})
        worker_list[job] = worker_info
    print worker_list
    return render_template('jobs/my_jobs.html', jobs=worker_list)


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
    accepting_job = Job.query.filter_by(job_id=job_id).all()[0]
    accepting_job.accepted_id = requestor_id
    db.session.commit()
    return redirect(url_for('jobs.my_jobs'))


@jobs.route('/review/<int:id>', methods=['GET', 'POST'])
@login_required
def review(id):
    current_job = Job.query.filter_by(id=id).all()
    form = ReviewJobForm()
    return render_template('jobs/review.html', job=current_job, form=form)
