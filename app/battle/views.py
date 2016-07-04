from flask import render_template, url_for, redirect
from flask_login import login_required, current_user
from .forms import BattleForm
from . import battle
from ..decorators import permission_required
from ..models import Battle, Image, Permission, Vote
from ..filters import filters
from .. import db


@battle.route("/")
def battles():
    battles = Battle.query.all()
    return render_template("battles/battles.html",
                           battles=battles,
                           battles_count=len(battles))


@battle.route("/<int:battle_id>", methods=('GET', 'POST'))
@login_required
def fight(battle_id):
    form = BattleForm()
    if form.validate_on_submit():
        raise NotImplementedError
    battle = Battle.query.filter_by(id=battle_id).first_or_404()
    image = Image.query.filter_by(id=battle.image_id).first_or_404()
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
    old_v = Vote.query.filter_by(battle=battle, voter=current_user).first()
    if old_v is not None:
        old_v.choice = choice
        db.session.add(old_v)
    else:
        v = Vote(battle=battle, voter=current_user, choice=choice)
        db.session.add(v)
    db.session.commit()
    return redirect(url_for('.battles', battle_id=battle_id))

