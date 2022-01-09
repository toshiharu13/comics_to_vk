import copy
import logging
import os
import random
import shutil
from pathlib import Path
from urllib.parse import urlparse
from urllib.parse import unquote

import requests
from environs import Env


def get_comics(random_comics_number):
    """
    Функция скачивания комикса
    :param random_comics_number: номер комикса
    :return: комментарий к комиксу, путь до скаченного файла
    """
    url = f'https://xkcd.com/{random_comics_number}/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    decode_response = response.json()
    logging.info(decode_response)

    comics_url = decode_response['img']
    commics_comment = decode_response['alt']
    file_name = get_filename_from_url(comics_url)

    comics_file_destination = Path.cwd() / 'comics' / file_name
    download_comics(comics_file_destination, comics_url)
    logging.info(f'download to {comics_url}')

    return commics_comment, comics_file_destination


def get_random_comics_number():
    """
    Функция получения ссылки на рандомный файл комикса
    :return: случайный номер комикса
    """
    url = 'https://xkcd.com/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    decode_response = response.json()
    logging.info(decode_response)

    last_comics_number = decode_response['num']
    random_comics_number = random.randint(0, last_comics_number)
    return random_comics_number


def download_comics(destination, url):
    """
    Функция скачивания файла комикса на жесткий диск
    :param destination: полный путь сохранения с именем файла
    :param url: источник скачивания
    :return: None
    """
    response = requests.get(url)
    response.raise_for_status()
    with open(destination, 'wb') as file:
        file.write(response.content)


def get_filename_from_url(url):
    """
    Функция получения имени файла из ссылки
    :param url: ссылка на скачиваемый файл
    :return: имя файла
    """
    parsed_url = urlparse(url)
    path_to_file = parsed_url.path
    file_name = os.path.split(path_to_file)[1]
    unquote(file_name, encoding='utf-8', errors='replace')
    return file_name


def get_wall_upload_server(url, access_token, group_id):
    """
    Функция получения адреса сервера загрузки для комикса
    :param url: адрес API VK
    :param access_token: VK ключ
    :param group_id: ID VK группы
    :return: адрес сервера для загрузки комикса
    """
    method = 'photos.getWallUploadServer'
    full_url = f'{url}/{method}'
    params = {
            'access_token': access_token,
            'group_id': group_id,
            'v': '5.131'
    }
    response = requests.get(full_url, params=params)
    response.raise_for_status()
    decode_response = response.json()
    check_for_error(decode_response)
    return decode_response['response']['upload_url']


def upload_comics(url, image):
    """
    функция загрузки изображения на сервер VK
    :param url: адрес API VK
    :param image: локальная ссылка на загружаемый комикс
    :return: данные для дальней обработки изображения(комикса)
    """
    with open(image, 'rb') as file:
        files = {
            'photo': file}
        response = requests.post(url, files=files)
    response.raise_for_status()
    decode_response = response.json()
    check_for_error(decode_response)
    return decode_response


def save_wall_photo(url, access_token, group_id, download_data):
    """
    Функция сохранения изображенияв альбом группы(с download сервера)
    :param url: адрес API VK
    :param access_token: VK ключ
    :param group_id: ID VK группы
    :param download_data: данные загрузки комикса на сервер
    :return: данные загрузки в альбом, необходимы для дальнейшего поста
    """
    params = {
        'access_token': access_token,
        'group_id': group_id,
        'v': '5.131',
        'server': download_data['server'],
        'photo': download_data['photo'],
        'hash': download_data['hash']
    }
    method = 'photos.saveWallPhoto'
    full_url = f'{url}/{method}'
    response = requests.post(full_url, params=params)
    response.raise_for_status()
    decode_response = response.json()
    check_for_error(decode_response)
    logging.info(decode_response)
    return decode_response


def create_wall_post(
        url, access_token, group_id, comics_message, response_save_wall):
    """
    Функция поста сообщения с изображением на стену
    :param url: адрес API VK
    :param access_token: VK токен
    :param group_id: VK ID группы
    :param comics_message: сообщение будущего поста
    :param response_save_wall: данные для параметров данного матода
    :return: номер поста в группе
    """
    params = {
        'access_token': access_token,
        'group_id': group_id,
        'v': '5.131',
        'message': comics_message,
        'from_group': 1,
        'owner_id': f'-{group_id}'
    }
    full_url = f'{url}/wall.post'
    media_owner_id = response_save_wall['response'][0]['owner_id']
    vk_comics_url_id = response_save_wall['response'][0]['id']
    attach_variable = f'photo{media_owner_id}_{vk_comics_url_id}'
    params['attachments'] = attach_variable

    response = requests.get(full_url, params=params)
    response.raise_for_status()
    decode_response = response.json()
    check_for_error(decode_response)
    return decode_response


def check_for_error(response):
    """
    Функция проверки ответа VK на ошибки
    :param response: ответ VK сервера
    :return: текст ошибки, если будет обнаружена ошибка
    """
    if 'error' in response:
        raise requests.exceptions.HTTPError(response['error'])


def main():
    env = Env()
    env.read_env()

    logging.basicConfig(
        level=logging.DEBUG,
        filename='log.lod',
        filemode='w',)
    comics_folder = Path.cwd() / 'comics'
    Path(comics_folder).mkdir(parents=True, exist_ok=True)
    vk_api_uri = 'https://api.vk.com/method'
    access_token = env.str('VK_TOKEN')
    group_id = env.str('VK_GROUP_ID')
    try:
        comics_number = get_random_comics_number()
        comics_message_and_image = get_comics(comics_number)
        uri_upload_server = get_wall_upload_server(
            vk_api_uri, access_token, group_id)
        logging.info(uri_upload_server)

        upload_response = upload_comics(
            uri_upload_server, comics_message_and_image[1])
        response_save_wall = save_wall_photo(
            vk_api_uri,  access_token, group_id, upload_response)
        logging.info(response_save_wall)

        response_create_post = create_wall_post(
            vk_api_uri, access_token, group_id, comics_message_and_image[0],
            response_save_wall)
        logging.info(response_create_post)
    except Exception as error:
        logging.info(f'Programm failed: {error}.')
    finally:
        shutil.rmtree(comics_folder, ignore_errors=True)


if __name__ == '__main__':
    main()
