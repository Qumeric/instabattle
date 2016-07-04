from flask import render_template
from flask_login import login_required
from .forms import BattleForm
from . import battle
from ..models import Battle, Image
from ..filters import filters


@battle.route("/")
def battles():
    battle_count = Battle.query.count()
    return render_template("battles/battles.html", count=battle_count)


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