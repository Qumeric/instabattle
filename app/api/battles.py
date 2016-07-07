from flask import request, jsonify, g
from ..schemas import battle_schema, battles_schema, vote_schema, challenge_schema
from . import api
from flask_login import login_required
from .decorators import permission_required
from ..models import Permission, Image, Battle


@api.route("/battles/")
def battles():
    battles = Battle.query.filter_by(challenge_accepted=True).all()
    return battles_schema.jsonify(battles), 200


@api.route("/battle/<int:id>", methods=['GET'])
def fight(id):
    battle = Battle.query.get_or_404(id)
    if not battle.challenge_accepted:
        return jsonify({'message': "Battle isn't accepted yes"}), 400
    return battle_schema.jsonify(battle)


@api.route("/battle/<int:battle_id>/<choice>")
@permission_required(Permission.VOTE)
def vote(battle_id, choice):
    battle = Battle.query.filter_by(id=battle_id).first_or_404()
    try:
        g.current_user.vote(battle=battle, choice=choice)
    except:
        return jsonify(
            {'message':
             'You cannot vote in this battle or vote is malformed'}), 422
    return redirect(request.args.get('next') or url_for('.battles',
                                                        _external=True)), 201


@api.route("/challenges")
@permission_required(Permission.CHALLENGE)
def challenges():
    challenges_in = g.current_user.challenged_by.filter_by(
        challenge_accepted=False).all()
    challenges_out = g.current_user.challenged_who.filter_by(
        challenge_accepted=False).all()
    json_in = battles_schema.dump(challenges_in)
    json_out = battles_schema.dump(challenges_out)
    return jsonify({'sent': json_out.data, 'recived': json_in.data}), 200


@api.route("accept/<int_id>/<int:is_accepted>")
def decide(id, is_accepted):
    battle = g.current_user.challenged_by.filter_by(id=id).first_or_404()
    try:
        battle = battle.decide(g.current_user, is_accepted)
    except:
        return jsonify(
            {'message': 'You cannot accept or decline this battle'}), 422
    if battle:  # accepted
        return redirect(url_for('.fight', id=battle.id, external=True)), 201
    else:  # declined
        return redirect(url_for('.challenges', _external=True)), 201
