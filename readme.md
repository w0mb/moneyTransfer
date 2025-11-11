# Money Transfer System

## https://bot-develop.ru/

приложение уже развернуто и запущено по этому адресу

## Python 3.14.0

## postgres 14 и выше

### 1. Клонирование репозитория

git clone <https://github.com/w0mb/moneyTransfer.git> .

### 2. Установка необходимого ПО
Скачайте Python с официального сайта: https://www.python.org/downloads/

Скачайте PostgreSQL с https://www.postgresql.org/download/

Создайте файл .env в корне проекта и добавьте:

DB_NAME=название предварительно созданной базы данных

DB_USER=пользователя базы данных

DB_PASSWORD=пароль от postgres

DB_HOST=localhost

DB_PORT=5432

DEBUG=True

## Запуск


### Вариант 1: Запуск через Docker(при наличии)

docker network create myNetwork

docker-compose build

docker-compose up db -d

docker-compose up money_service -d


### Вариант 2: Обычный запуск

python -m venv venv

cd venv\Scripts\

.\activate

pip install -r requirements.txt


в корне проекта django:

python manage.py makemigrations

python manage.py migrate

python manage.py createsuperuser

python manage.py runserver


приложение будет доступно по адресу:

Главная страница: http://127.0.0.1:8000

Админ-панель: http://127.0.0.1:8000/admin/
