from flask import current_app
from flask_wtf import FlaskForm as Form
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length, NumberRange


class CreateJobForm(Form):
    name = StringField('Job Name', validators=[DataRequired(), Length(1, 500)])
    description = StringField('Description', validators=[DataRequired(), Length(1, 300)])
    street_name = StringField('Street Name', validators=[DataRequired(), Length(1, 64)])
    zip_code = IntegerField('Zip Code', validators=[DataRequired()])
    submit = SubmitField('Create Job')


class ReviewJobForm(Form):
    rating = IntegerField('Rating (1-5)', validators=[DataRequired(), Length(1, 1)])
    review = StringField('Review', validators=[DataRequired(), Length(1, 500)])
    submit = SubmitField('Submit Review')
