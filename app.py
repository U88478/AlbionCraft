from flask import Flask
from app.routes import bp

from models import init_app


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///models/albion_items.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    init_app(app)
    app.register_blueprint(bp)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='127.0.0.1', port=8000)
