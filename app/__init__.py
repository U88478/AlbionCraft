import os

from flask import Flask

from app.extensions import db, migrate
from app.routes import bp as routes_bp


def create_app():
    app = Flask(__name__, template_folder='templates')

    # Get the absolute path of the database file
    basedir = os.path.abspath(os.path.dirname(__file__))
    database_path = os.path.join(basedir, '..', 'models', 'albion_items.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(routes_bp)

    # Print the path where Flask is looking for templates and database
    print(f"Looking for templates in: {app.template_folder}")
    print(f"Using database file at: {database_path}")

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='127.0.0.1', port=8000)
