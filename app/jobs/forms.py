from flask import current_app
from flask_wtf import FlaskForm as Form
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length, ValidationError

class Len(object):
    def __init__(self, num=5, message=None):
        self.num = num
        if not message:
            message = u'Field must be %i characters long.' % num
        self.message = message

    def __call__(self, form, field):
        if len(str(field.data)) != self.num:
            raise ValidationError(self.message)

class CreateJobForm(Form):
    name = StringField('Job Name', validators=[DataRequired(), Length(1, 64)])
    description = StringField('Description', validators=[DataRequired(), Length(1, 500)])
    street_name = StringField('Street Name', validators=[DataRequired(), Length(1, 64)])
    zip_code = IntegerField('Zip Code', validators=[DataRequired(message="Please Enter a Zip Code"), Len(5)])
    submit = SubmitField('Create Job')


class ReviewJobForm(Form):
    rating = IntegerField('Rating (1-5)', validators=[DataRequired(), Length(1, 1)])
    review = StringField('Review', validators=[DataRequired(), Length(1, 500)])
    submit = SubmitField('Submit Review')

class ZipFilterForm(Form):
    zip_code = IntegerField('Zip Code:', validators=[DataRequired(message="Please Enter a Zip Code"), Len(5)])
    submit = SubmitField('Filter')