import os
import random
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv
from loguru import logger


VK_API_URL = 'https://api.vk.com/method/'


def fetch_xkcd_comic(
        image_path: str,
        image_link: str,
        directory: str) -> None:
    """Fetch xkcd comic image into determined directory."""
    Path(directory).mkdir(exist_ok=True)
    response = requests.get(image_link)
    response.raise_for_status()
    with open(image_path, 'wb') as img_file:
        img_file.write(response.content)


def get_upload_server(token: str, api_version: str) -> str:
    """Return upload server params."""
    params = {
        'access_token': token,
        'v': api_version,
    }
    response = requests.get(f'{VK_API_URL}photos.getWallUploadServer', params)
    response.raise_for_status()
    return response.json()


def load_comic(url: str, image_path: str) -> dict:
    """
    Move comic on VK-server and return photo url, server_id and
    photo_hash.
    """
    with open(image_path, 'rb') as img_file:
        files = {
            'photo': img_file,
        }
        response = requests.post(url, files=files)
    response.raise_for_status()
    return response.json()


def save_image_on_server(
        photo: str,
        server_id: int,
        image_hash: str,
        comic_comment: str,
        token: str,
        api_version: str) -> dict:
    """Save comic image on server and return saved image params."""
    params = {
        'photo': photo,
        'server': server_id,
        'hash': image_hash,
        'caption': comic_comment,
        'access_token': token,
        'v': api_version,
    }
    response = requests.post(f'{VK_API_URL}photos.saveWallPhoto', params)
    response.raise_for_status()
    return response.json()


def post_comic(
        group_id: int,
        from_group: int,
        owner_id: int,
        media_id: int,
        post_title: str,
        token: str,
        api_version: str,
        ) -> None:
    """Post comic in VK-public."""
    params = {
        'owner_id': group_id,
        'from_group': from_group,
        'attachments': f'photo{owner_id}_{media_id}',
        'message': post_title,
        'access_token': token,
        'v': api_version,
    }
    response = requests.post(f'{VK_API_URL}wall.post', params)
    response.raise_for_status()


def get_xkcd_comic(comic_number=None) -> dict:
    """Return xkcd comic in json format."""
    if comic_number is None:
        response = requests.get('https://xkcd.com/info.0.json')
        response.raise_for_status()
        return response.json()
    response = requests.get(f'https://xkcd.com/{comic_number}/info.0.json')
    response.raise_for_status()
    return response.json()


@logger.catch
def main() -> None:
    """Post random xkcd comic in VK-public."""
    logger.add(
        sys.stderr,
        format='[{time:HH:mm:ss}] <lvl>{message}</lvl>',
        level='ERROR'
    )
    load_dotenv()
    token = os.getenv('VK_TOKEN')
    group_id = os.getenv('VK_GROUP_ID')
    vk_api_version = '5.131'
    comic_number = random.randint(1, int(get_xkcd_comic()['num']))
    images_directory = 'images'
    xkcd_comic = get_xkcd_comic(comic_number=comic_number)
    image_path = Path(images_directory, f'xkcd_comic_{comic_number}.png')
    fetch_xkcd_comic(
        image_path=image_path,
        image_link=xkcd_comic['img'],
        directory=images_directory
    )

    try:
        upload_server_params = get_upload_server(
            token=token,
            api_version=vk_api_version
        )
        upload_url = upload_server_params['response']['upload_url']
        photo_on_server = load_comic(
            url=upload_url,
            image_path=image_path
        )

        saved_image = save_image_on_server(
            photo=photo_on_server['photo'],
            server_id=photo_on_server['server'],
            image_hash=photo_on_server['hash'],
            comic_comment=xkcd_comic['alt'],
            token=token,
            api_version=vk_api_version,
        )

        post_comic(
            group_id=-int(group_id),
            from_group=1,
            owner_id=saved_image['response'][0]['owner_id'],
            media_id=saved_image['response'][0]['id'],
            post_title=xkcd_comic['title'],
            token=token,
            api_version=vk_api_version,
        )
    except requests.exceptions.HTTPError:
        logger.error(
            'Ошибка обработки HTTP запроса, попробуйте перезапустить скрипт'
        )
        sys.exit(1)
    finally:
        os.remove(image_path)


if __name__ == '__main__':
    main()
