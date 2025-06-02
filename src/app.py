from flask import Flask
from flask_cors import CORS
from api.routes import api_bp  # маршруты API (например, events.py)
from extensions import mail, db, login_manager

# === Создание приложения ===
app = Flask(__name__)
app.config['SECRET_KEY'] = 'my-secret-key'  # использует Flask-Login
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Namigra_20@localhost:5432/schedule_db?options=-c search_path=schedule_app,public'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'yurastep05@gmail.com'
app.config['MAIL_PASSWORD'] = 'Namigra_2020'

# === Подключение CORS (для фронта) ===
CORS(app, supports_credentials=True)

# === Инициализация базы данных, LoginManager и mail ===
db.init_app(app)
mail.init_app(app)
login_manager.init_app(app)

# === Импорт моделей (чтобы SQLAlchemy знал о них) ===
from models.models import User  # обязательно импортировать модели

# === Обязательная функция для Flask-Login ===
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# === Подключение API ===
app.register_blueprint(api_bp, url_prefix='/api')

# === Точка входа ===
if __name__ == '__main__':
    app.run(debug=True)