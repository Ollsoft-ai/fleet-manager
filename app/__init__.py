import os
from flask import Flask, request, session

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'dev-key-for-development')
    if not app.config['SECRET_KEY']:
        raise ValueError("No SECRET_KEY set for Flask application")
    
    # Set the environment
    app.config['FLASK_ENV'] = os.environ.get('FLASK_ENV', 'production')

    if app.config['FLASK_ENV'] == 'development':
        app.config['DEBUG'] = True

    # Register Blueprints
    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
