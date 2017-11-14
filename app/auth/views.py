from app import db
from app.models import User
from app.email import send_email
from ..auth import auth
from ..auth.forms import (
    LoginForm,
    RegistrationForm,
    PasswordResetForm,
    PasswordResetRequestForm,
    ChangePasswordForm
)

from flask import render_template, current_app, redirect, request, url_for, flash, session
from flask_login import login_required, login_user, logout_user, current_user
from datetime import datetime
from werkzeug.security import check_password_hash


@auth.route('/register', methods=['GET', 'POST'])
def register():
    """
    Renders the HTML page where users can register new accounts. If the RegistrationForm meets criteria, a new user is
    written into the database.

    :return: HTML page for registration.
    """
    form = RegistrationForm()
    print(form)
    if form.validate_on_submit():
        user = User(email=(form.email.data).lower(),
                    password=form.password.data,
                    first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    validated=True)
        db.session.add(user)
        db.session.commit()
        flash('User successfully registered!', category='success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    View function to login a user. Redirects the user to the index page on successful login.

    :return: Login page.
    """
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=(form.email.data).lower()).first()

        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            db.session.add(user)
            db.session.commit()
            current_app.logger.info('{} successfully logged in'.format(current_user.email))
            return redirect(url_for('main.index'))

        else:
            flash('Invalid username or password!', category='error')
            return redirect(url_for('auth.login'))

    return render_template('auth/login.html', form=form, reset_url=url_for('auth.password_reset_request'))


@auth.route('/logout')
@login_required
def logout():
    """
    View function to logout a user.

    :return: Index page.
    """
    logout_user()
    flash('You have been logged out.', category='success')
    return redirect(url_for('auth.login'))


@auth.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    """
    View function for changing a user password.

    :return: Change Password page.
    """
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if check_password_requirements(current_user.email, form.old_password.data, form.password.data,
                                       form.password2.data):
            current_user.password_list.update(current_user.password_hash)
            current_user.password = form.password.data
            current_user.validated = True
            db.session.add(current_user)
            db.session.commit()
            current_app.logger.info('{} changed their password.'.format(current_user.email))
            flash('Your password has been updated.', category='success')
            return redirect(url_for('main.index'))

    return render_template("auth/change_password.html", form=form)


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    """
    View function for requesting a password reset.

    :return: HTML page in which users can request a password reset.
    """
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))

    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=(form.email.data).lower()).first()

        if user:
            token = user.generate_reset_token()
            send_email(user.email, 'Reset Your Password', 'auth/email/reset_password', user=user, token=token,
                       next=request.args.get('next'))
            flash('An email with instructions to reset your password has been sent to you.', category='success')

        else:
            flash('An account with this email was not found in the system.', category='error')

        return redirect(url_for('auth.login'))
    return render_template('auth/request_reset_password.html', form=form)
