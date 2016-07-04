from flask_wtf import Form
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms import ValidationError
from wtforms.validators import Required, Email, Length
from ..models import User


class RegisterForm(Form):
    email = StringField("Email",
                        validators=[Required(), Email(), Length(1, 120)])
    password = PasswordField("Password", validators=[Required()])
    submit = SubmitField("Register")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("Email has already been taken")


class LoginForm(Form):
    email = StringField("Email",
                        validators=[Required(), Email(), Length(1, 120)])
    password = PasswordField("Password", validators=[Required()])
    remember_me = BooleanField("Remember me")
    submit = SubmitField("Login")


class PasswordResetRequestForm(Form):
    email = StringField('Email',
                        validators=[Required(), Length(1, 120), Email()])
    submit = SubmitField('Reset Password')


class PasswordResetForm(Form):
    email = StringField('Email',
                        validators=[Required(), Length(1, 120), Email()])
    password = PasswordField('New Password', validators=[Required()])
    submit = SubmitField('Reset Password')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('Unknown email address.')
