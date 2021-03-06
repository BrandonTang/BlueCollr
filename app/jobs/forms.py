from flask import current_app
from flask_wtf import FlaskForm as Form
from wtforms import StringField, SubmitField, IntegerField, DecimalField, SelectField
from wtforms.validators import DataRequired, Length, ValidationError
from wtforms.widgets import TextArea


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
    zip_code = IntegerField('Zip Code', validators=[DataRequired(message="Please enter a zip code."), Len(5)])
    price = DecimalField('Price', places=2,
                         validators=[DataRequired(message="Please specify a price you are requesting.")])
    submit = SubmitField('Create Job')


class ReviewJobForm(Form):
    rating = SelectField('Rating (1-5)', choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')])
    review = StringField('Review', validators=[DataRequired(), Length(1, 500)], widget=TextArea())
    submit = SubmitField('Submit')


class ZipFilterForm(Form):
    zip_code = IntegerField('', validators=[DataRequired(message="Please enter a zip code."), Len(5)])
    submit = SubmitField('Filter')


class PriceForm(Form):
    price = DecimalField('My Price:', places=2,
                         validators=[DataRequired(message="Please specify a price you are charging.")])
    submit = SubmitField('Request')
