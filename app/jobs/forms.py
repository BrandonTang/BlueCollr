from flask import current_app
from flask_wtf import FlaskForm as Form
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length


class CreateJobForm(Form):
    name = StringField('Job Name', validators=[DataRequired(), Length(1, 64)])
    description = StringField('Email', validators=[DataRequired(), Length(1, 300)])
    street_name = StringField('Street Name', validators=[DataRequired(), Length(1, 64)])
    zip_code = IntegerField('Zip Code', validators=[DataRequired(), Length(5, 5)])
    submit = SubmitField('Create Job')
