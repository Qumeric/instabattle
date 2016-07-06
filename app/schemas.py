from . import ma
from .models import Vote, Battle, User, Image


def hyperlink(endpoint, external=True, **kwargs):
    return ma.HyperlinkRelated(endpoint, external=True, **kwargs)


class VoteSchema(ma.ModelSchema):
    class Meta:
        model = Vote


class BattleSchema(ma.ModelSchema):
    class Meta:
        model = Battle

    image = hyperlink('api.show_image')
    challenger = hyperlink('api.user')
    challenged = hyperlink('api.user')
    _links = ma.Hyperlinks({
        'self': ma.URLFor('api.fight', id='<id>',
                          _external=True),
        'collection': ma.URLFor('api.battles', _external=True)
    },
                           dump_only=True)


class UserSchema(ma.ModelSchema):
    class Meta:
        model = User
        fields = ('username', 'email', 'name', 'member_since', 'last_seen',
                  'images', 'challenged_by', 'challenged_who', 'votes',
                  '_links')

    email = ma.Email(load_only=True)
    images = ma.List(hyperlink('api.show'))
    challenged_who = ma.List(hyperlink('api.user'))
    challenged_by = ma.List(hyperlink('api.user'))
    _links = ma.Hyperlinks({'self': ma.URLFor('api.user',
                                              id='<id>',
                                              _external=True)},
                           dump_only=True)


class ImageSchema(ma.ModelSchema):
    class Meta:
        model = Image

    user = hyperlink('api.user')
    battles = ma.List(hyperlink('api.fight'))
    _links = ma.Hyperlinks({'self': ma.URLFor('api.show_image',
                                              id='<id>',
                                              _external=True),
                            'collection':
                            ma.URLFor('api.show', _external=True)},
                           dump_only=True)


# FIXME unused
class ChallengeSchema(ma.Schema):
    sent = ma.Nested(BattleSchema, many=True)
    recived = ma.Nested(BattleSchema, many=True)


image_schema = ImageSchema()
images_schema = ImageSchema(many=True)
user_schema = UserSchema()
users_schema = UserSchema(many=True)
vote_schema = VoteSchema()
votes_schema = VoteSchema(many=True)
battle_schema = BattleSchema()
battles_schema = BattleSchema(many=True)
challenge_schema = ChallengeSchema()
