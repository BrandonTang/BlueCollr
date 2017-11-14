from app import db
from app.models import Job, JobRequestor
from ..jobs import jobs
from ..jobs.forms import CreateJobForm, ReviewJobForm

from flask import render_template
from flask_login import login_required, current_user


@jobs.route('/<int:id>', methods=['GET', 'POST'])
@login_required
def job(id):
    chosen_job = Job.query.filter_by(id=id).all()
    return render_template('jobs/job.html', job=chosen_job)


@jobs.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = CreateJobForm()
    if form.validate_on_submit():
        job = Job(name=form.name.data,
                  description=form.description.data,
                  status="Pending",
                  creator_id=current_user.id)
        db.session.add(job)
        db.session.commit()
        flash('Job successfully created!', category='success')
        return redirect(url_for('jobs.browse'))
    return render_template('jobs/create.html', form=form)


@jobs.route('/browse', methods=['GET', 'POST'])
@login_required
def browse():
    all_jobs = Job.query.all()
    return render_template('jobs/browse.html', jobs=all_jobs)


@jobs.route('/my_jobs', methods=['GET', 'POST'])
@login_required
def my_jobs():
    job_list = Job.query.filter_by(creator_id=current_user.id).all()
    worker_list = {}
    for job in job_list:
        current_job = job.id
        all_workers = JobRequestor.query.filter_by(job_id=current_job)
        worker_list[job] = all_workers
    return render_template('jobs/my_jobs.html', jobs=worker_list)


@jobs.route('/accept/<int:requestor_id>/<int:job_id>', methods=['GET', 'POST'])
@login_required
def accept(requestor_id, job_id):
    accepting_job = Job.query.filter_by(job_id=job_id)
    accepting_job.accepted_id = requestor_id
    db.session.commit()
    return redirect(url_for('jobs.my_jobs'))


@jobs.route('/review/<int:id>', methods=['GET', 'POST'])
@login_required
def review(id):
    current_job = Job.query.filter_by(id=id).all()
    form = ReviewJobForm()
    return render_template('jobs/review.html', job=current_job, form=form)
