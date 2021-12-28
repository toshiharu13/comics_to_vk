# Постим чеоез VK API комиксы
Программа для публикации комиксов из xkcd.com в VK группе

[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)

## Техническое описание
Данная программа при запуске публикиет рандомный комикс из коллекции сайта  https://xkcd.com, и выкладывает на стене группы в https://vk.com

## Как установить
- Cклонировать проект

```git clone https://github.com/toshiharu13/comics_to_vk.git```

- Установить requirements.txt

```pip install -r requirements.txt```

- Создать файл .env и заполнить в нем переменные:

   - ```VK_APP_ID=<ID вашей группы, в которой вы будете выкладывать комиксы>```
   - ```VK_TOKEN=<токен для доступа к VK API>```

## Запуск

```python3 main.py```
## Цель проекта
Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [Devman](https://dvmn.org).