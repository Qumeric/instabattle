from flask import Blueprint

battle = Blueprint('battle', __name__)

from . import views, forms
