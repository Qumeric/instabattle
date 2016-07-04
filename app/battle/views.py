from flask import render_template
from flask_login import login_required
from .forms import BattleForm
from . import battle
from ..decorators import permission_required
from ..models import Battle, Image, Permission
from ..filters import filters


@battle.route("/")
def battles():
    battles = Battle.query.all()
    return render_template("battles/battles.html",
                           battles=battles,
                           battles_count=len(battles))


@battle.route("/<int:battle_id>", methods=('GET', 'POST'))
@login_required
def battle(battle_id):
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
