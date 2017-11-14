from app import db
from ..jobs import jobs
from ..jobs.forms import CreateJobForm

from flask import render_template
from flask_login import login_required, current_user


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
