from flask import render_template, url_for, redirect, flash, abort, request
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
    return render_template("battles/battles.html", battles=battles)


@battle.route("/<int:id>", methods=('GET', 'POST'))
@login_required
def fight(id):
    filter = ""
    battle = Battle.query.get_or_404(id)
    is_challenger = (battle.challenger_id == current_user.id)
    is_challenged = (battle.challenged_id == current_user.id)
    if is_challenger:
        filter = battle.challenger_filter
    elif is_challenged:
        filter = battle.challenged_filter
    form = BattleForm(filter = filter)

    if not battle.challenge_accepted:
        flash("This battle isn't accepted yet")
        return redirect(url_for('.battles'))
    if form.validate_on_submit():
        filter = form.filter.data
        print('Filter:', filter)
        if is_challenger:
            battle.challenger_filter = filter
            battle.challenger_finished = True
        elif is_challenged:
            battle.challenged_filter = filter
            battle.challenged_finished = True
        else:
            flash("Unknown user")
            return redirect(url_for('.battles'))
        db.session.add(battle)
        db.session.commit()

    return render_template("battles/battle.html",
                           battle=battle,
                           form=form,
                           filter=filter
                           )


@battle.route("/vote/<int:battle_id>/<choice>")
@login_required
@permission_required(Permission.VOTE)
def vote(battle_id, choice):
    battle = Battle.query.filter_by(id=battle_id).first_or_404()
    try:
        current_user.vote(battle=battle, choice=choice)
    except:
        flash("You can't vote in this battle")
    return redirect(request.args.get('next') or url_for('.fight',
                                                        id=battle_id))


@battle.route("/challenges")
@login_required
def challenges():
    challenges_out = current_user.challenged_who.filter_by(
        challenge_accepted=False).all()
    challenges_in = current_user.challenged_by.filter_by(
        challenge_accepted=False).all()
    return render_template("battles/challenges.html",
                           incoming=challenges_in,
                           waiting=challenges_out)


@battle.route("/accept/<int:id>/<int:is_accepted>")
@login_required
def decide(id, is_accepted):
    battle = current_user.challenged_by.filter_by(id=id).first_or_404()
    try:
        battle = battle.decide(current_user, is_accepted)
    except:
        flash("You cannot accept or decline this battle")
        return redirect(url_for('.battles'))
    if battle:  # accepted
        return redirect(url_for('.fight', id=battle.id))
    else:  # declined
        return redirect(url_for('.challenges'))
