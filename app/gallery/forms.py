from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms import ValidationError
from wtforms.validators import Required, Email
from ..models import User


class ChallengeForm(Form):
    email = StringField("Email", validators=[Required(), Email()])
    submit = SubmitField("Challenge")

    def validate_email(self, field):
        if not User.query.filter_by(email=field.data).first():
            raise ValidationError('There are no users with such email')
