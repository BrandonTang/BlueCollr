from ..models import User

from flask import current_app
from flask_wtf import FlaskForm as Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class EditForm(Form):
    """Used to register new users into the system."""
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    first_name = StringField("First name")
    last_name = StringField("Last name")
    # password = PasswordField('Password', validators=[
    #     DataRequired(), EqualTo('password2', message='Passwords must match')])
    # password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Edit')

    def validate_email(self, email_field):
        """
        Verifies that e-mails used for registration do not already exist in the system.

        :param email_field:
        :return:
        """
        user = User.query.filter_by(email=email_field.data).first()
        if user:
            if user.email:
                current_app.logger.error('{} tried to register user with email {} but user already exists.'.format(
                    user.email, email_field.data))
            else:
                current_app.logger.error('Anonymous user tried to register user with email {} but user already exists.'.
                                         format(email_field.data))
            raise ValidationError('An account with this email address already exists')

    # def validate_password(self, password_field):
    #     """
    #     Used to verify that password meets security criteria.
    #
    #     :param password_field: password field
    #     :return: A validation message if password is not secure.
    #     """
    #     if len(password_field.data) < 8:
    #         raise ValidationError('Your password must be 8 or more characters')
    #
    #     has_num = False
    #     has_capital = False
    #     for i in password_field.data:
    #         if i.isdigit():
    #             has_num = True
    #         if i.isupper():
    #             has_capital = True
    #
    #     if not (has_num or has_capital):
    #         raise ValidationError('Passwords must contain at least one number and one capital letter')
    #
    #     if not has_num:
    #         raise ValidationError('Password must contain at least one number')
    #
    #     if not has_capital:
    #         raise ValidationError('Password must contain at least one capital letter')