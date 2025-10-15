import os
from flask import Flask
from .extensions import db, login_manager

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'sua-chave-secreta-aqui'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Blueprint de autenticação
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # Blueprint principal
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    return app
