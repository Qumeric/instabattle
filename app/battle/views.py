from flask import render_template, url_for, redirect, flash, abort
from flask_login import login_required, current_user
from .forms import BattleForm
from . import battle
from ..decorators import permission_required
from ..models import Battle, Image, Permission, Vote
from ..filters import filters
from .. import db


@battle.route("/")
def battles():
    battles = Battle.query.filter_by(challenge_accepted=True).all()
    return render_template("battles/battles.html",
                           battles=battles,
                           battles_count=len(battles))


@battle.route("/<int:battle_id>", methods=('GET', 'POST'))
@login_required
def fight(battle_id):
    form = BattleForm()
    battle = Battle.query.filter_by(id=battle_id).first_or_404()
    if not battle.challenge_accepted:
        flash("This battle isn't accepted yet")
        return redirect(url_for('.battles'))
    image = Image.query.filter_by(id=battle.image_id).first_or_404()
    if form.validate_on_submit():
        raise NotImplementedError
    return render_template("battles/battle.html",
                           battle=battle,
                           image=image,
                           form=form,
                           filters=filters)

@battle.route("/vote/<int:battle_id>/<choice>")
@login_required
@permission_required(Permission.VOTE)
def vote(battle_id, choice):
    battle = Battle.query.filter_by(id=battle_id).first()
    if not battle.challenge_accepted:
        abort(403)
    old_v = Vote.query.filter_by(battle=battle, voter=current_user).first()
    if old_v is not None:
        old_v.choice = choice
        db.session.add(old_v)
    else:
        v = Vote(battle=battle, voter=current_user, choice=choice)
        db.session.add(v)
    db.session.commit()
    return redirect(url_for('.battles', battle_id=battle_id))

@battle.route("/challenges")
@login_required
def challenges():
    challenges_out = current_user.challenged_who.filter_by(challenge_accepted=False).all()
    challenges_in = current_user.challenged_by.filter_by(challenge_accepted=False).all()
    return render_template("battles/challenges.html", incoming=challenges_in, waiting=challenges_out)

@battle.route("accept/<int:battle_id>/<int:accepted>")
@login_required
def decide(battle_id, accepted):
    battle = current_user.challenged_by.filter_by(id=battle_id).first_or_404()
    if current_user != battle.challenged:
        flash("You cannot accept or decline this battle")
        return redirect(url_for('.battles'))
    if accepted:
        battle.challenge_accepted = True
        db.session.add(battle)
    else:
        db.session.delete(battle)

    db.session.commit()
    return redirect(url_for('.battles'))
