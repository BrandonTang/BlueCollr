from ..models import User

from flask import current_app
from flask_wtf import FlaskForm as Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class EditForm(Form):
    """Used to register new users into the system."""
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    first_name = StringField("First Name")
    last_name = StringField("Last Name")
    submit = SubmitField('Edit')

    # def validate_email(self, email_field):
    #     """
    #     Verifies that e-mails used for registration do not already exist in the system.
    #
    #     :param email_field:
    #     :return:
    #     """
    #     user = User.query.filter_by(email=email_field.data).first()
    #     if user:
    #         if user.email:
    #             current_app.logger.error('{} tried to register user with email {} but user already exists.'.format(
    #                 user.email, email_field.data))
    #         else:
    #             current_app.logger.error('Anonymous user tried to register user with email {} but user already exists.'.
    #                                      format(email_field.data))
    #         raise ValidationError('An account with this email address already exists')
