from flask_wtf import Form
from wtforms import SubmitField


class BattleForm(Form):
    submit = SubmitField("Submit")
