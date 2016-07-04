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
    if current_user.can(Permission.CHALLENGE) and form.validate_on_submit():
        challenged_user = User.query.filter_by(email=form.email.data).first()
        try:
            battle = current_user.challenge(challenged_user.id, image_id)
        except ValueError:
            flash("You cannot challenge yourself!")
        else:
            flash("Let the battle begin!")
            return redirect(url_for('battle.battle', battle_id = battle.id))
                
    user = current_user._get_current_object()
    image = Image.query.filter_by(id=image_id).first_or_404()
    return render_template("gallery/show_image.html", image=image, form=form, user=user)

