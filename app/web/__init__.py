from flask import Flask
from flask_login import LoginManager

from app.db.database import db, close_db_connection, init_db
from app.models import User

login_manager = LoginManager()
login_manager.login_view = 'web.login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object('config.Config')
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    # Register blueprints
    from app.api.routes import api_bp
    from app.web.routes import web_bp
    
    app.register_blueprint(api_bp)
    app.register_blueprint(web_bp)
    
    # Initialize database
    with app.app_context():
        init_db()
    
    # Register teardown function
    @app.teardown_appcontext
    def cleanup(exc):
        close_db_connection()
    
    return app

__version__ = '0.2.0'