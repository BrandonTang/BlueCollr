from flask import current_app
from flask_wtf import FlaskForm as Form
from wtforms import StringField, SubmitField, IntegerField, DecimalField, RadioField
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
    price = DecimalField('Price', places=2, validators=[DataRequired(message="Please specify a price you are requesting")])
    submit = SubmitField('Create Job')


class StarField(RadioField):
    def __init__(self, *args, **kwargs):
        super(StarField, self).__init__(*args, **kwargs)
        self.label = 'Rating (1-5)'
        self.choices = [('5', '5'), ('4', '4'), ('3', '3'), ('2', '2'), ('1', '1')]
        self.validators = [DataRequired()]

    def __str__(self):

        ans = '<span class="star-cb-group">'

        for choice in self.choices:
            ans += '<input type="radio" id="rating-' + choice[0] + \
                   '" name="rating" value="' + choice[0] + \
                   '" /><label for="rating-' + choice[0] + \
                   '">' + choice[0] + '</label>'
        ans += '</span>'
        return ans

    def __call__(self):

        ans = '<span class="star-cb-group">'

        for choice in self.choices:
            ans += '<input type="radio" id="rating-' + choice[0] + \
                   '" name="rating" value="' + choice[0] + \
                   '" /><label for="rating-' + choice[0] + \
                   '">' + choice[0] + '</label>'
        ans += '</span>'
        return ans


class ReviewJobForm(Form):
    def __init__(self, *args, **kwargs):
        super(ReviewJobForm, self).__init__(*args, **kwargs)

    # rating = RadioField('Rating (1-5)', choices=[('5', '5'), ('4', '4'), ('3', '3'), ('2', '2'), ('1', '1')])
    rating = StarField()
    review = StringField('Review', validators=[DataRequired(), Length(1, 500)])
    submit = SubmitField('Submit Review')


class ZipFilterForm(Form):
    zip_code = IntegerField('Zip Code:', validators=[DataRequired(message="Please Enter a Zip Code"), Len(5)])
    submit = SubmitField('Filter')


class PriceForm(Form):
    price = DecimalField('My Price:', places=2, validators=[DataRequired(message="Please specify a price you are charging")])
    submit = SubmitField('Request')