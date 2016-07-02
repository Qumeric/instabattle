from flask_wtf import Form
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms import ValidationError
from wtforms.validators import Required, Email
from ..models import User


class RegisterForm(Form):
    email = StringField("Email", validators=[Required(), Email()])
    password = PasswordField("Password", validators=[Required()])
    submit = SubmitField("Register")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError("Email has already been taken")


class LoginForm(Form):
    email = StringField("Email", validators=[Required(), Email()])
    password = PasswordField("Password", validators=[Required()])
    remember_me = BooleanField("Remember me")
    submit = SubmitField("Login")
