import copy
import logging
import os
import random
import shutil
from pathlib import Path
from urllib.parse import urlparse

import requests
from environs import Env


def get_comics(url):
    """
    Функция скачивания комикса
    :param url: ссылка на комикс
    :return: комментарий к комиксу, путь до скаченного файла
    """
    response = requests.get(url)
    response.raise_for_status()
    logging.info(response.json())
    comics_url = response.json()['img']
    commics_comment = response.json()['alt']
    file_name = get_filename_from_url(comics_url)
    copy_destination = Path.cwd()/'comics'/file_name
    download_comics(copy_destination, comics_url)
    logging.info(f'download to {comics_url}')
    return commics_comment, copy_destination


def get_random_comics_link(url):
    """
    Функция получения ссылки на рандомный файл комикса
    :param url: ссылка на последний комикс
    :return: ссылка на рандомный комикс
    """
    response = requests.get(url)
    response.raise_for_status()
    logging.info(response.json())
    last_comics_number = response.json()['num']
    int_random = random.randint(0, last_comics_number)
    return f'https://xkcd.com/{int_random}/info.0.json'


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
    parse_url = urlparse(url)
    path_to_file = parse_url.path
    file_name = os.path.split(path_to_file)[1]
    return file_name


def get_wall_upload_server(url, params):
    """
    Функция получения адреса сервера загрузки для комикса
    :param url: адрес API VK
    :param params: стандартные параметры, корректируются под каждую функцию
    :return: адрес сервера для загрузки комикса
    """
    method = 'photos.getWallUploadServer'
    full_url = f'{url}/{method}'
    response = requests.get(full_url, params=params)
    response.raise_for_status()
    logging.info(response.json())
    return response.json()['response']['upload_url']


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
        return response.json()


def save_wall_photo(url, params, download_data):
    """
    Функция сохранения изображенияв альбом группы(с download сервера)
    :param url: адрес API VK
    :param params: стандартные параметры, корректируются под каждую функцию
    :param download_data: данные загрузки комикса на сервер
    :return: данные загрузки в альбом, необходимы для дальнейшего поста
    """
    method = 'photos.saveWallPhoto'
    params_local = copy.copy(params)
    (params_local['server'],
     params_local['photo'],
     params_local['hash']) = (download_data['server'],
                              download_data['photo'],
                              download_data['hash'])
    full_url = f'{url}/{method}'
    response = requests.post(full_url, params=params_local)
    response.raise_for_status()
    logging.info(response.json())
    return response.json()


def create_wall_post(url, params, comics_message, response_save_wall):
    """
    Функция поста сообщения с изображением на стену
    :param url: адрес API VK
    :param params: стандартные параметры, корректируются под каждую функцию
    :param comics_message: сообщение будущего поста
    :param response_save_wall: данные для параметров данного матода
    :return: номер поста в группе
    """
    full_url = f'{url}/wall.post'
    params_local = copy.copy(params)
    params_local['message'] = comics_message
    params_local['from_group'] = 1
    group_id = params['group_id']
    params_local['owner_id'] = f'-{group_id}'
    media_owner_id = response_save_wall['response'][0]['owner_id']
    vk_comics_url_id = response_save_wall['response'][0]['id']
    attach_variable = f'photo{media_owner_id}_{vk_comics_url_id}'
    params_local['attachments'] = attach_variable
    response = requests.get(full_url, params=params_local)
    response.raise_for_status()
    return response.json()


def clear_image_folder(folder):
    """
    Функия очистки папки с изображениями
    :param folder: папка которую надо чистить(для гибгости)
    :return: None
    """
    try:
        shutil.rmtree(folder)
    except Exception as e:
        logging.info('Failed to delete %s. Reason: %s' % (folder, e))


def main():
    env = Env()
    env.read_env()

    logging.basicConfig(
        level=logging.DEBUG,
        filename='log.lod',
        filemode='w',)
    current_comics_json_url = 'https://xkcd.com/info.0.json'
    comics_folder = Path.cwd() / 'comics'
    Path(comics_folder).mkdir(parents=True, exist_ok=True)
    vk_api_uri = 'https://api.vk.com/method'
    vk_url_params = {
        'access_token': env.str('VK_TOKEN'),
        'group_id': 207675974,
        'v': '5.131'}

    randon_comics_link = get_random_comics_link(current_comics_json_url)
    comics_message_and_image = get_comics(randon_comics_link)
    uri_download_server = get_wall_upload_server(vk_api_uri, vk_url_params)
    logging.info(uri_download_server)
    donload_data = upload_comics(uri_download_server,
                                 comics_message_and_image[1])
    response_save_wall = save_wall_photo(vk_api_uri, vk_url_params,
                                         donload_data)
    logging.info(response_save_wall)
    response_create_post = create_wall_post(vk_api_uri, vk_url_params,
                                            comics_message_and_image[0],
                                            response_save_wall)
    logging.info(response_create_post)
    clear_image_folder(comics_folder)


if __name__ == '__main__':
    main()
