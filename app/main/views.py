import os
from uuid import uuid4
from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import login_required
from .forms import UploadForm
from . import main
from ..models import Image, User
from .. import db
from flask_login import current_user


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
        image = Image(name=filename, user_id=current_user.id)
        db.session.add(image)
        db.session.commit()
        flash("Your image has been loaded")
        return redirect(url_for('main.index'))
    return render_template("upload.html", form=form)

@main.route("/user/<username>")
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template("user.html", user=user)
