import logging
from pathlib import Path
import requests
from urllib.parse import urlparse
import os
from environs import Env


def get_vk_request(url, params, method):
    full_uri = f'{url}/{method}'
    response = requests.get(full_uri, params=params)
    response.raise_for_status()
    logging.info(response.text)
    return response.json()


def get_comics(url):
    response = requests.get(url)
    response.raise_for_status()
    logging.info(response.json())
    comics_url = response.json()['img']
    commics_comment = response.json()['alt']
    file_name = get_filename_from_url(comics_url)
    copy_destination = Path.cwd()/'comics'/file_name
    download_comics(copy_destination, comics_url)
    logging.info(f'download {comics_url}')
    return commics_comment


def download_comics(destination, url):
    response = requests.get(url)
    response.raise_for_status()
    with open(destination, 'wb') as file:
        file.write(response.content)


def get_filename_from_url(url):
    parse_url = urlparse(url)
    path_to_file = parse_url.path
    file_name = os.path.split(path_to_file)[1]
    return file_name


def get_wall_upload_server(url, params, method):
    full_url = f'{url}/{method}'
    response = requests.get(full_url, params=params)
    response.raise_for_status()
    logging.info(response.json())
    return response.json()['response']['upload_url']


'''def download_image(url, image):
    with open(image, 'rb') as file:
        files = {
            'media': file,}
        response = requests.post(url, files=files)
        response.raise_for_status()
        return response.json()'''


def save_wall_photo(url, params, method):
    full_url = f'{url}/{method}'
    response = requests.post(full_url, params=params)
    response.raise_for_status()
    logging.info(response.json())
    return response.json()


if __name__ == '__main__':
    env = Env()
    env.read_env()

    logging.basicConfig(
        level=logging.DEBUG,
        filename='log.lod',
        filemode='w',
    )
    current_comics_json_url = 'https://xkcd.com/info.0.json'
    comics_folder = Path.cwd()/'comics'
    Path(comics_folder).mkdir(parents=True, exist_ok=True)
    vk_app_id = env.str('VK_APP_ID')
    vk_api_uri = 'https://api.vk.com/method'
    vk_url_params = {
        'access_token': env.str('VK_TOKEN'),
        'group_id': 207675974,
        'v': '5.131'}
    photo = f'{comics_folder}/immunity.png'
    method_get_server = 'photos.getWallUploadServer'
    method_save_image = 'photos.saveWallPhoto'

    uri_download_server = get_wall_upload_server(vk_api_uri, vk_url_params, method_get_server)
    logging.info(uri_download_server)
    print(uri_download_server)
    #print(download_image(uri_download_server, photo))
    #print(save_wall_photo(uri_download_server, vk_url_params, method_save_image))


