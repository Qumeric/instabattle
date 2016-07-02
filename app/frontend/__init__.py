from flask import Blueprint
from flask_nav import Nav
from flask_nav.elements import Navbar, View
from flask_login import current_user

# FIXME is it needed?
from ..main import main
from ..auth import auth

nav = Nav()


def frontend_nav():
    navbar = Navbar('', (View("Instabattle", 'main.index')), )
    navbar.items = list(navbar.items)

    if current_user.is_authenticated:
        navbar.items.append(View("Log Out", 'auth.logout'))
    else:
        navbar.items.append(View("Log In", 'auth.login'))
        navbar.items.append(View("Register", 'auth.register'))

    return navbar


frontend = Blueprint('frontend', __name__)

nav.register_element('frontend_top', frontend_nav)
