from flask import Flask

from config import Config
from models import init_app as init_db


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    init_db(app)

    from app.routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    return app
