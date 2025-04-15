import os
from datetime import timedelta

class Config:
    """Base configuration."""
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    FLASK_APP = 'app.main'
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///data/crud-app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # API
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'dev-jwt-secret')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_ECHO = True

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    
    # In production, ensure proper secret keys are set
    def __init__(self):
        if self.SECRET_KEY == 'dev-secret-key':
            raise ValueError('SECRET_KEY environment variable must be set in production')
        if self.JWT_SECRET_KEY == 'dev-jwt-secret':
            raise ValueError('JWT_SECRET_KEY environment variable must be set in production')