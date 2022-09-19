# Платформа для блогов Yatube

Проект социальной сети Yatube. Реализована возможность создания учетной записи, публикации, редактирования и удаления постов, подписки на других пользователей, добавления комментариев к постам. Посты могут содержать изображения и текст. Также они могут быть объединены в сообщества. 
Есть возможность вступить в сообщество.
Доступна общая лента всей сети и персональная лента подписок

## Технологии:

* Python 3.7
* Django framework 2.2.16
* HTML
* CSS (Bootstrap 3)
* Djangorestframework-simplejwt 

## Как запустить проект:


Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/SenkoAlina/hw05_final.git
```

Cоздать и активировать виртуальное окружение:

```
python -m venv env
```

```
source env/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python manage.py migrate
```

Запустить проект:

```
python manage.py runserver


