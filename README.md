__Описание.__
Проект foodgram это сайт, где пользователь может публиковать свои рецепты, подписываться на других пользователей, добавлять рецепты в избранное, добавлять рецепты в список покупок (при этом будет посчитано какие ингдедиенты и в каком количестве необходимо приобрести). 

__Установка. Как запустить проект.__
Клонировать репозиторий и перейти в него в командной строке:

*git clone git@github.com:poli-na-96/foodgram.git* 
*cd foodgram*

Cоздать и активировать виртуальное окружение, потом перейти в папку backend:

*python3 -m venv venv source venv/Scripts/activate*
*cd backend*

Установить зависимости из файла requirements.txt:

*pip install -r requirements.txt*

Запустить проект:

*docker compose -f infra/docker-compose.yml up --build*

Проект будет доступен локально по адресу: https://localhost:8081

__Примеры запросов.__
*Запрос на создание рецепта:*

http://localhost:8081/api/recipes/
{
"ingredients": [
{}
],
"tags": [
1,
2
],
"image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
"name": "string",
"text": "string",
"cooking_time": 1
}

*Ответ:*
{
"id": 0,
"tags": [
{}
],
"author": {
"email": "user@example.com",
"id": 0,
"username": "string",
"first_name": "Вася",
"last_name": "Иванов",
"is_subscribed": false,
"avatar": "http://foodgram.example.org/media/users/image.png"
},
"ingredients": [
{}
],
"is_favorited": true,
"is_in_shopping_cart": true,
"name": "string",
"image": "http://foodgram.example.org/media/recipes/images/image.png",
"text": "string",
"cooking_time": 1
}

*Запрос на регистрацию пользователя.*
http://localhost:8081/api/users/
{
  "email": "vpupkin@yandex.ru",
  "username": "vasya.pupkin",
  "first_name": "Вася",
  "last_name": "Иванов",
  "password": "Qwerty123"
}

*Ответ:*
{
  "email": "vpupkin@yandex.ru",
  "id": 0,
  "username": "vasya.pupkin",
  "first_name": "Вася",
  "last_name": "Иванов"
}

__Cодержимое env-файла для запуска.__
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=1234kg
DB_NAME=foodgram
DB_HOST=db
DB_PORT=5432
SECRET_KEY='django-insecure-cg6*%6d51ef8f#4!r3*$vmxm4567'
DEBUG=False
ALLOWED_HOSTS='158.160.17.163,127.0.0.1,localhost:8081,myfoodgramm.hopto.org'

__Cпособ запуска миграций.__
При запущенном проекте на локальной машине в новом терминале последовательно выполните команды:
docker compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py migrate

__Стек технологий, использованных в проекте:__
python, django, postgres, nginx, docker, docker compose, git, CI/CD

__Автор проекта:__
Путилина Полина, *github: poli-na-96*

__Данные для доступа в админ-зону:__
email: ppv96@yandex.ru password: Gjkkb1996

Проект доступен по доменному имени: *https://myfoodgramm.hopto.org*

