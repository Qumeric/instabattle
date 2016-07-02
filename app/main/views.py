from flask import render_template, session, redirect, url_for, flash
from . import main
from .forms import RegisterForm, LoginForm
from .. import db
from ..models import User


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            user = User(email=form.email.data)
            db.session.add(user)
            db.session.commit()
            print("A new user have successfully registred")
        else:
            flash("Email has been taken")
        return redirect(url_for('.index'))
    return render_template('register.html', form=form)


@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None:
            print(user, "is not None")
            print("Saved password:", user.password)
            print("Entered password:", form.password.data)
        if user is None and user.password == form.password.data:  # FIXME unsecure
            session['email'] = form.email.data
            return redirect(url_for('.index'))
        else:
            flash("You have entered an invalid email or password")
    return render_template('login.html', form=form)
