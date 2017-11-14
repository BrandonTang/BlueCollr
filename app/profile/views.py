from app import db
from app.models import User, Role
from app.decorators import admin_required
from app.email import send_email
from ..profile import profile
# from ..profile.forms import (
#
# )

from flask import render_template, current_app, redirect, request, url_for, flash, session
from flask_login import login_required, login_user, logout_user, current_user
from datetime import datetime
from werkzeug.security import check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


@profile.route('/<user_id>', methods=['GET', 'POST'])
def profile(user_id):
    """

    """

    user = User.query.filter_by(id=user_id).first()
    # form = RegistrationForm()
    # print(form)
    # if form.validate_on_submit():
    #     user = User(email=(form.email.data).lower(),
    #                 password=form.password.data,
    #                 first_name=form.first_name.data,
    #                 last_name=form.last_name.data,
    #                 validated=True)
    #     db.session.add(user)
    #     db.session.commit()
    #     flash('User successfully registered', category='success')
    #     return redirect(url_for('auth.login'))
    return render_template('profile/profile.html', user=user)
