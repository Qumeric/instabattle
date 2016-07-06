from flask import Flask
from flask_bootstrap import Bootstrap, WebCDN
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_marshmallow import Marshmallow
from flask_debugtoolbar import DebugToolbarExtension
from config import config
from random import choice

bootstrap = Bootstrap()
db = SQLAlchemy()
mail = Mail()
ma = None # A hack
toolbar = DebugToolbarExtension()

login_manager = LoginManager()
login_manager.session_protected = 'strong'
login_manager.login_view = 'auth.login'

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)
    bootstrap.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    toolbar.init_app(app)
    global ma
    ma = Marshmallow(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix="/auth")

    from .frontend import frontend as frontend_blueprint
    app.register_blueprint(frontend_blueprint)

    from .gallery import gallery as gallery_blueprint
    app.register_blueprint(gallery_blueprint, url_prefix="/gallery")

    from .battle import battle as battle_blueprint
    app.register_blueprint(battle_blueprint, url_prefix="/battles")

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    from .frontend import nav
    nav.init_app(app)

    app.extensions['bootstrap']['cdns']['jquery'] = WebCDN(
        '//cdnjs.cloudflare.com/ajax/libs/jquery/2.2.4/'  # Use jquery 2
    )

    return app
