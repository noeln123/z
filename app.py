from flask import Flask
from config import Config
from extensions import db, login_manager, socketio
from routers import user_bp, admin_bp, emt_bp
from flask_migrate import Migrate
from models import Setting

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Khởi tạo các tiện ích
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'user.login'
    login_manager.login_message_category = 'info'
    migrate = Migrate(app, db)

    # Khởi tạo socketio
    socketio.init_app(app, cors_allowed_origins="*") 
    
    # Đăng ký blueprints
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(emt_bp, url_prefix='/emt')

    # Import các models để Flask-Migrate có thể nhận diện chúng
    with app.app_context():
        from models import User, Profile, Ambulance, Driver, EmergencyRequest, Feedback
        # db.create_all()  # just first-run or use Flask-Migrate
        auto_dispatch = Setting.query.filter_by(key='auto_dispatch').first()
        if not auto_dispatch:
            auto_dispatch = Setting(key='auto_dispatch', value='False')
            db.session.add(auto_dispatch)
            db.session.commit()

    return app

app = create_app()

if __name__ == '__main__':
    socketio.run(app, debug=True)