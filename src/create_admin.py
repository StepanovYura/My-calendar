from extensions import db
from models.models import User
from werkzeug.security import generate_password_hash
def create():
    # Задаём данные
    name = "Admin"
    email = "admin@example.com"
    password = "admin"
    privacy_setting = "all"
    role = "admin"

    # Хешируем пароль
    password_hash = generate_password_hash(password)

    # Создаем объект пользователя
    admin_user = User(
        name=name,
        email=email,
        password_hash=password_hash,
        privacy_setting=privacy_setting,
        role=role
    )

    # Добавляем в сессию и коммитим
    db.session.add(admin_user)
    db.session.commit()

    print(f"Админ создан: {admin_user.id}, {admin_user.email}")

if __name__ == "__main__":
    from app import app  # Импортируйте ваш Flask app
    with app.app_context():
        create()