from app import db
from app.models import User
from ..profile import profile
from ..profile.forms import (
    EditForm
)

from flask import render_template, current_app, redirect, request, url_for, flash, session
from flask_login import login_required, login_user, logout_user, current_user


@profile.route('/<user_id>', methods=['GET', 'POST'])
@login_required
def view_profile(user_id):
    user = User.query.filter_by(id=user_id).first()
    return render_template('profile/profile.html', user=user)


@profile.route('/<user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_profile(user_id):
    form = EditForm()
    user = User.query.filter_by(id=user_id).first()
    if form.validate_on_submit():
        # Get info from form
        user_first_name = form.first_name.data
        user_last_name = form.last_name.data
        user_email = form.email.data

        # Modify the database
        current_user.first_name = user_first_name
        current_user.last_name = user_last_name
        current_user.email = user_email

        db.session.commit()
        flash('User information successfully updated!')
        return redirect(url_for('profile.view_profile', user_id=user.id))
    return render_template('profile/edit.html', form=form, user=user)
