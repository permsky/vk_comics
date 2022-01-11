import os
import random
from pathlib import Path

import requests
from dotenv import load_dotenv


def get_image_link(url: str) -> str:
    """Return link on comic image."""
    response = requests.get(url)
    response.raise_for_status()
    return response.json()['img']


def get_comic_number(url: str) -> int:
    """Return comic image number."""
    response = requests.get(url)
    response.raise_for_status()
    return int(response.json()['num'])


def download_image(url: str, image_name: str) -> None:
    """Download image from url."""
    response = requests.get(url)
    response.raise_for_status()
    with open(image_name, 'wb') as img:
        img.write(response.content)


def fetch_xkcd_comic(url: str, directory: str, image_number: int) -> None:
    """Fetch xkcd comic image into determined directory."""
    image_link = get_image_link(url)
    Path(directory).mkdir(exist_ok=True)
    image_name = f'{directory}xkcd_comic_{image_number}.png'
    download_image(image_link, image_name)


def get_xkcd_comic_comment(url: str) -> str:
    """Return author comment."""
    response = requests.get(url)
    response.raise_for_status()
    return response.json()['alt']


def get_upload_server(url: str, params: dict) -> str:
    """Return upload server params."""
    response = requests.get(url, params)
    response.raise_for_status()
    return response.json()


def load_comic(url: str, directory: str, image_number: int) -> dict:
    """
    Move comic on VK-server and return photo url, server_id and
    photo_hash.
    """
    with open(f'{directory}xkcd_comic_{image_number}.png', 'rb') as file:
        files = {
            'photo': file,
        }
        response = requests.post(url, files=files)
        response.raise_for_status()
    return response.json()


def delete_comic_image(directory: str, image_number: int) -> None:
    """Delete comic image from local directory."""
    os.remove(f'{directory}xkcd_comic_{image_number}.png')


def save_image_on_server(url: str, params: dict) -> dict:
    """Save comic image on server and return saved image params."""
    response = requests.post(url, params)
    response.raise_for_status()
    return response.json()


def post_comic(url: str, params: dict) -> None:
    """Post comic in VK-public."""
    response = requests.post(url, params)
    response.raise_for_status()


if __name__ == '__main__':
    load_dotenv()
    token = os.getenv('VK_TOKEN')
    vk_api_version = '5.131'
    comic_number = random.randint(
        1,
        get_comic_number('https://xkcd.com/info.0.json')
    )
    xkcd_comic_url = (f'https://xkcd.com/{comic_number}/info.0.json')
    images_directory = './images/'
    response = requests.get(xkcd_comic_url)
    response.raise_for_status()
    xkcd_comic = response.json()
    title = xkcd_comic['title']
    image_number = get_comic_number(xkcd_comic_url)
    fetch_xkcd_comic(xkcd_comic_url, images_directory, image_number)

    get_params = {
        'access_token': token,
        'v': vk_api_version,
    }
    vk_upload_server_url = (
        'https://api.vk.com/method/photos.getWallUploadServer'
    )

    upload_server_params = get_upload_server(vk_upload_server_url, get_params)
    upload_url = upload_server_params['response']['upload_url']
    photo_on_server = load_comic(upload_url, images_directory, image_number)

    delete_comic_image(images_directory, image_number)

    vk_save_image_url = 'https://api.vk.com/method/photos.saveWallPhoto'
    save_params = {
        'photo': photo_on_server['photo'],
        'server': photo_on_server['server'],
        'hash': photo_on_server['hash'],
        'caption': get_xkcd_comic_comment(xkcd_comic_url),
        'access_token': token,
        'v': vk_api_version,
    }
    saved_image = save_image_on_server(vk_save_image_url, save_params)

    post_url = 'https://api.vk.com/method/wall.post'
    media_id = saved_image['response'][0]['id']
    owner_id = saved_image['response'][0]['owner_id']
    post_params = {
        'owner_id': -210058270,
        'from_group': 1,
        'attachments': f'photo{owner_id}_{media_id}',
        'message': title,
        'access_token': token,
        'v': vk_api_version,
    }
    post_comic(post_url, post_params)
