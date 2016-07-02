from flask import render_template, session, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from . import auth
from .forms import RegisterForm, LoginForm
from . import auth
from .. import db
from ..models import User

@auth.route("/register", methods=('GET', 'POST'))
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("You can login now")
        return redirect(url_for('auth.login'))
    return render_template("auth/register.html", form=form)


@auth.route("/login", methods=('GET', 'POST'))
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash("You have entered an invalid email or password")
    return render_template("auth/login.html", form=form)

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out")
    return redirect(url_for('main.index'))
