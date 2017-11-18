from app import db
from app.models import User, Job
from ..profile import profile
from ..profile.forms import (
    EditForm
)

from flask import render_template, current_app, redirect, request, url_for, flash, session
from flask_login import login_required, login_user, logout_user, current_user
from ..constants import status


@profile.route('/<user_id>', methods=['GET', 'POST'])
@login_required
def view_profile(user_id):
    user = User.query.filter_by(id=user_id).first()
    jobs_completed = Job.query.filter_by(accepted_id=user_id, status=status.COMPLETED)
    return render_template('profile/profile.html', user=user, jobs_completed=jobs_completed)


@profile.route('/<user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_profile(user_id):
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
        db.session.commit()

        flash('User information successfully updated!')
        return redirect(url_for('profile.view_profile', user_id=user.id))
    return render_template('profile/edit.html', form=form, user=user)
