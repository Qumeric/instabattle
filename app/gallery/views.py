from flask import render_template, flash, url_for, redirect
from flask_login import current_user, login_required
from . import gallery
from ..models import Image, User, Battle, Permission
from .. import db
from .forms import ChallengeForm


@gallery.route("/")
def show():
    images = Image.query.limit(12)
    return render_template("gallery/show.html", images=images)

@gallery.route("/image/<int:image_id>", methods=('GET', 'POST'))
@login_required
def show_image(image_id):
    form = ChallengeForm()
    image = Image.query.filter_by(id=image_id).first_or_404()
    user = current_user._get_current_object() # FIXME do I need it?
    if current_user.can(Permission.CHALLENGE) and form.validate_on_submit():
        challenged_user = User.query.filter_by(email=form.email.data).first()
        if challenged_user is None:
            flash("There are no such user")
            return render_template("gallery/show_image.html", image=image, form=form, user=user)
        try:
            battle = user.challenge(challenged_user, image)
        except ValueError:
            flash("You cannot challenge yourself!")
        else:
            flash("Let the battle begin!")
            return redirect(url_for('battle.fight', battle_id = battle.id))
                
    return render_template("gallery/show_image.html", image=image, form=form, user=user)

