from app import db
from app.models import User, Job
from ..profile import profile
from ..profile.forms import EditForm


from flask import render_template, current_app, redirect, request, url_for, flash, session
from flask_login import login_required, current_user
from ..constants import status
import os
import datetime


@profile.route('/<user_id>', methods=['GET', 'POST'])
@login_required
def view_profile(user_id):
    user = User.query.filter_by(id=user_id).first()
    jobs_completed = Job.query.filter_by(accepted_id=user_id, status=status.COMPLETED)
    if user.picture_path is None:
        pic_path = "/static/img/userpics/default_pic.png"
    else:
        pic_path = user.picture_path
        print pic_path
    return render_template('profile/profile.html', pic_path=pic_path, user=user, jobs_completed=jobs_completed)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

@profile.route('/<user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_profile(user_id):
    if current_user.id == int(user_id):
        form = EditForm()
        user = User.query.filter_by(id=user_id).first()
        if request.method == 'GET':
            # Pre-populate form
            form.first_name.data = user.first_name
            form.last_name.data = user.last_name
            form.email.data = user.email

        if form.validate_on_submit():
            # Get info from form and modify
            if form.first_name != user.first_name:
                current_user.first_name = form.first_name.data
            if form.last_name != user.last_name:
                current_user.last_name = form.last_name.data
            if form.email != user.email:
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
                path = os.path.join(current_app.config['UPLOAD_FOLDER'], str(user_id) + "_" + str(microseconds) + "_pic" + ext)
                print path
                f.save(path)
                old_path = current_user.picture_path
                os.remove('./app' + old_path)
                current_user.picture_path = path[5:]
            db.session.commit()
            flash('User information successfully updated!')
            return redirect(url_for('profile.view_profile', user_id=user.id))

        return render_template('profile/edit.html', form=form, user=user)

    flash('Do not try to edit other peoples profiles!')
    return redirect(url_for('profile.view_profile', user_id=user_id))
