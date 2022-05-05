# Тестовый Джанго-проект (Yatube) (Яндекс.Практикум)

Технологии:
- Python 3.7
- Django 2.2.6

Инструкция по запуска:
- Склонировать проект
- Установить виртуальное окружение ```python -m venv venv```
- Установить зависимости внутри окружения ```pip install -r requirements.txt```
- Перейти в директорию yatube ```cd yatube```
- Создать и выполнить миграции ```python manage.py makemigrations``` -> ```python manage.py migrate```
- Запустить сервер ```python manage.py runserver```
- Сервер доступен по адресу ```127.0.0.1:8000/```