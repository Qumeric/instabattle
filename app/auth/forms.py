from flask_wtf import Form
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms import ValidationError
from wtforms.validators import Required, Email, Length, Regexp
from ..models import User


class RegisterForm(Form):
    email = StringField("Email",
                        validators=[Required(), Email(), Length(1, 120)])
    username = StringField("Username",
                             validators=[
                                 Required(), Length(1, 64),
                                 Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                        'Usernames must have only letters, '
                                        'numbers, dots or underscores')
                             ])
    password = PasswordField("Password", validators=[Required()])
    submit = SubmitField("Register")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("Email has already been taken")

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError("Username has already been taken")


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
