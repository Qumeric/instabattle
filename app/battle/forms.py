from flask_wtf import Form
from wtforms import SubmitField, SelectField
from ..filters import filters


class BattleForm(Form):
    filter = SelectField("filter", choices=filters)
    submit = SubmitField()
