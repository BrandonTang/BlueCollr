from app import db
from app.models import User, Job
from ..profile import profile
from ..profile.forms import EditForm


from flask import render_template, current_app, redirect, request, url_for, flash, session
from flask_login import login_required, login_user, logout_user, current_user
from ..constants import status
import os


@profile.route('/<user_id>', methods=['GET', 'POST'])
@login_required
def view_profile(user_id):
    user = User.query.filter_by(id=user_id).first()
    jobs_completed = Job.query.filter_by(accepted_id=user_id, status=status.COMPLETED).all()
    if user.picture_path is None:
        pic_path = "/static/img/userpics/default_pic.png"
    else:
        pic_path = user.picture_path
    return render_template('profile/profile.html', pic_path=pic_path, user=user, jobs_completed=jobs_completed)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


@profile.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditForm()
    # user = User.query.filter_by(id=user_id).first()

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
            path = os.path.join(current_app.config['UPLOAD_FOLDER'], str(current_user.id) + "_pic" + ext)
            f.save(path)
            current_user.picture_path = path[5:]
        db.session.commit()

        flash('User information successfully updated!')
        return redirect(url_for('profile.view_profile', user_id=current_user.id))
    return render_template('profile/edit.html', form=form, user=current_user)
