from flask import Flask
from .config import Config
from .models import db
from app.routes.leads import bp as leads_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():
        db.create_all()
    
    app.register_blueprint(leads_bp, url_prefix="/api")

    return app
