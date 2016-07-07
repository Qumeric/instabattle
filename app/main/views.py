import os
from uuid import uuid4
from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import login_required
from flask_sqlalchemy import get_debug_queries
from .forms import UploadForm
from . import main
from ..models import Image, User, Battle
from .. import db
from flask_login import current_user


@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config['SLOW_DB_QUERY_TIME']:
            current_app.logger.warning(
                'Slow query: {}\nParameters: {}\nDuration: %{}s\nContext: %{}\n'.format(
                    query.statement, query.parameters, query.duration,
                    query.context))
    return response


@main.route("/")
def index():
    return render_template("index.html")


@main.route("/upload", methods=('GET', 'POST'))
@login_required
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        file = request.files['image']
        filename = uuid4().hex
        file.save(os.path.join(current_app.config['UPLOAD_DIR'], filename))
        image = Image(name=filename,
                      user_id=current_user.id)  # FIXME user, not id?
        db.session.add(image)
        db.session.commit()
        flash("Your image has been loaded")
        return redirect(url_for('main.index'))
    return render_template("upload.html", form=form)


# FIXME
@main.route("/user/<int:id>")
@main.route("/user/<username>")
def user(username=None, id=None):
    if username:
        user = User.query.filter_by(username=username).first_or_404()
    if id:
        user = User.query.get_or_404(id)
    battles = user.battles.filter_by(challenge_accepted=True).all()
    return render_template("user.html", user=user, battles=battles)
