from flask import Blueprint
from flask_nav import Nav
from flask_nav.elements import Navbar, View
from flask_login import current_user

nav = Nav()


def frontend_nav():
    navbar = Navbar('', (View("Instabattle", 'main.index')), )
    navbar.items = list(navbar.items)

    if current_user.is_authenticated:
        navbar.items.append(View("Log Out", 'auth.logout'))
        navbar.items.append(View("Upload", 'main.upload'))
    else:
        navbar.items.append(View("Log In", 'auth.login'))
        navbar.items.append(View("Register", 'auth.register'))

    return navbar


frontend = Blueprint('frontend', __name__)

nav.register_element('frontend_top', frontend_nav)
