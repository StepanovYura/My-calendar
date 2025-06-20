from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
from api.routes import api_bp  # маршруты API (например, events.py)
from extensions import mail, db, jwt
import os

# === Создание приложения ===
# static_folder = папка с собранным фронтом
app = Flask(__name__, static_folder='dist', static_url_path='')
app.config['SECRET_KEY'] = 'my-secret-key'  # использует Flask-Login
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://myappuser:MyAppUserStrongPassword@YuraSt-4632.postgres.pythonanywhere-services.com:14632/myappdb'  # os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/schedule_db').replace('postgres://', 'postgresql://')#'postgresql://postgres:Namigra_20@localhost:5432/schedule_db?options=-c search_path=schedule_app,public'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'yurastep05@gmail.com'
app.config['MAIL_PASSWORD'] = 'Namigra20' # или Namigra20 # НУЖЕН НЕ ОБЫЧНЫЙ ПАРОЛЬ А СГЕНЕРИРОВАННЫЙ ОТ GOOGLE В APP-PASSWORD
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'avatars')
# === Подключение CORS (для фронта) ===
CORS(app, resources={r"/api/*": {"origins": "*"}}) #CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})

# === Инициализация базы данных, jwt и mail ===
db.init_app(app)
jwt.init_app(app)
mail.init_app(app)

# === Импорт моделей (чтобы SQLAlchemy знал о них) ===
from models.models import User  # обязательно импортировать модели

# === Подключение API ===
app.register_blueprint(api_bp, url_prefix='/api')

# === Обработка фронтенда (Vue) ===
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_vue(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

# === Точка входа ===
if __name__ == '__main__':
    app.run()