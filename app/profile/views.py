from app import db
from app.models import User, Job
from ..profile import profile
from ..profile.forms import EditForm
from ..constants import status
from ..utils import allowed_file

import os
import datetime
from flask import render_template, current_app, redirect, request, url_for, flash, session
from flask_login import login_required, current_user


@profile.route('/<user_id>', methods=['GET', 'POST'])
@login_required
def view_profile(user_id):
    user = User.query.filter_by(id=user_id).first()
    jobs_completed = Job.query.filter_by(accepted_id=user_id, status=status.COMPLETED).all()

    # Find avg rating of completed jobs
    total = 0
    for job in jobs_completed:
        total += job.rating
    if len(jobs_completed) >= 1:
        avg_rating = "{0:.2f}".format(float(total) / len(jobs_completed))
    else:
        avg_rating = 0

    return render_template('profile/profile.html', user=user, jobs_completed=jobs_completed, avg_rating=avg_rating)


@profile.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditForm()

    if request.method == 'GET':
        # Pre-populate form
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.email.data = current_user.email

    if form.validate_on_submit():
        # Get info from form and modify
        if form.first_name != current_user.first_name:
            current_user.first_name = form.first_name.data
        if form.last_name != current_user.last_name:
            current_user.last_name = form.last_name.data
        if form.email != current_user.email:
            current_user.email = form.email.data
        if form.file.data is not None:
            f = form.file.data
            if f.mimetype == "image/png":
                ext = ".png"
            elif f.mimetype == "image/jpg":
                ext = '.jpg'
            elif f.mimetype == "image/jpeg":
                ext = '.jpeg'
            time_now = datetime.datetime.now()
            microseconds = time_now.microsecond
            path = os.path.join(current_app.config['UPLOAD_FOLDER'], str(current_user.id) + "_"
                                + str(microseconds) + "_pic" + ext)
            f.save(path)
            old_path = current_user.picture_path
            current_user.picture_path = path[5:]
            if old_path != "/static/img/userpics/default_pic.png":
                os.remove('./app' + old_path)
        db.session.commit()

        flash('User information successfully updated!')
        return redirect(url_for('profile.view_profile', user_id=current_user.id))

    return render_template('profile/edit.html', form=form, user=current_user)
