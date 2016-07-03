from flask import Blueprint
from flask_nav import Nav
from flask_nav.elements import Navbar, View
from flask_login import current_user

nav = Nav()


def frontend_nav():
    navbar = Navbar('', View("Instabattle", 'main.index'),
                         View("Gallery", 'gallery.show'),)
    navbar.items = list(navbar.items) # FIXME should be fixed in nav 0.6

    if current_user.is_authenticated:
        navbar.items.append(View("Log Out", 'auth.logout'))
        navbar.items.append(View("Upload", 'main.upload'))
    else:
        navbar.items.append(View("Log In", 'auth.login'))
        navbar.items.append(View("Register", 'auth.register'))

    navbar.items.append(View("Battles", 'battle.battles'))

    return navbar


frontend = Blueprint('frontend', __name__)

nav.register_element('frontend_top', frontend_nav)
