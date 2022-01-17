import requests
import json
import time
from tqdm import tqdm

with open('token.txt', 'r') as file_object:
    token = file_object.read().strip()


class VkUser:
    url = 'https://api.vk.com/method/'

    def __init__(self, token, version):
        self.params = {
            'access_token': token,
            'v': version
        }

    def search_profile_photo(self, owner_id=None, num_of_photos=5):
        profile_photo_search_url = self.url + 'photos.get'
        profile_photo_search_params = {
            'owner_id': owner_id,
            'album_id': 'profile',
            'photo_sizes': 1,
            'extended': 1
        }
        req = requests.get(profile_photo_search_url, params={**self.params, **profile_photo_search_params}).json()
        if 'error' in req.keys():
            print(req['error']['error_msg'])
            return
        else:
            photos = req['response']['items']
            photo_size_list = []
            for value in photos:
                if num_of_photos != 0:
                    current_photo = {}
                    current_photo['likes'] = value['likes']['count']
                    current_photo['date'] = value['date']
                    num_sizes = len(value['sizes'])
                    current_photo['url'] = value['sizes'][num_sizes - 1]['url']
                    current_photo['size'] = value['sizes'][num_sizes - 1]['type']
                    photo_size_list.append(current_photo)
                    num_of_photos -= 1
                else:
                    break
        return photo_size_list


class YaUploader:
    def __init__(self, token: str):
        self.token = token

    def create_folder(self):
        """Метод создает папку на яндекс диске"""
        folder_name = input('Введите название папки для создания на Я.диске: ')
        url = "https://cloud-api.yandex.net/v1/disk/resources"
        headers = {'Content-Type': 'application/json', 'Authorization': F'OAuth {self.token}'}
        params = {'path': folder_name}
        requests.put(url, headers=headers, params=params)
        return folder_name

    def upload(self, photo_list):
        """Метод загружает файлы на яндекс диск"""
        folder_name = self.create_folder()
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        headers = {'Content-Type': 'application/json', 'Authorization': F'OAuth {self.token}'}
        uploaded_photos = []
        info_for_json = []
        for photo in tqdm(photo_list):
            time.sleep(0.5)
            current_photo = {}
            if photo['likes'] not in uploaded_photos:
                file_name = f'{photo["likes"]}.jpg'
                params = {"path": f'{folder_name}/{file_name}', "url": photo['url']}
                uploaded_photos.append(photo['likes'])
                current_photo['file_name'] = file_name
            else:
                file_name = f'{photo["likes"]}_{photo["date"]}.jpg'
                params = {"path": f'{folder_name}/{file_name}.jpg', "url": photo['url']}
                current_photo['file_name'] = file_name
            current_photo['size'] = photo['size']
            info_for_json.append(current_photo)
            response_upload = requests.post(upload_url, headers=headers, params=params)
            response_upload.raise_for_status()
            #if response_upload.status_code == 202:
            #    print(f"Загружена фотография: {current_photo['file_name']}")
        print('Загрузка завершена')
        return info_for_json

    def create_result_file(self, data):
        with open('result.json', 'w', encoding='utf8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    vk_client = VkUser(token, '5.131')
    user_id = input('Введите ID пользователя: ')
    token = input('Введите ваш токен: ')
    num_of_photos = int(input('Введите количество фотографий для загрузки: '))
    photo_list = vk_client.search_profile_photo(user_id, num_of_photos)
    if photo_list is not None:
        uploader = YaUploader(token)
        result = uploader.upload(photo_list)
        uploader.create_result_file(result)
