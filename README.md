# Постим через VK API комиксы
Программа для публикации комиксов из [xkcd.com](https://xkcd.com) в [vk.com](https://vk.com) группе

[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)

## Техническое описание
Данная программа при запуске публикиет рандомный комикс из коллекции сайта  [xkcd.com](https://xkcd.com), и выкладывает его на стене группы в [vk.com](https://vk.com)

## Как установить
- Cклонировать проект

```git clone https://github.com/toshiharu13/comics_to_vk.git```

- Установить requirements.txt

```pip install -r requirements.txt```

- Создать файл .env и заполнить в нем переменные:

 ```VK_TOKEN=<токен для доступа к VK API>```

 - Для получения токена, необходимо завести адрес в браузере

```https://oauth.vk.com/authorize?client_id=<ID вашего приложения>&display=page&scope=photos,groups,wall,offline&response_type=token&v=5.131```

## Запуск

```python3 main.py```
## Цель проекта
Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [Devman](https://dvmn.org).