import requests
import json
import os.path
from pprint import pprint
from dotenv import load_dotenv
from tqdm import tqdm
import logging
logging.basicConfig(level=logging.INFO, filename="py_log.log",filemode="w")
logging.debug("A DEBUG Message")
logging.info("An INFO")
logging.warning("A WARNING")
logging.error("An ERROR")
logging.critical("A message of CRITICAL severity")

dotenv_path = 'config.env'
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

vk_token = os.getenv("VK_TOKEN")
ya_token = os.getenv("YA_TOKEN")

class VKConnector:
    def __init__(self, access_token, version = '5.199'):
        self.access_token = access_token
        self.version = version
        self.base_url = 'https://api.vk.com/method/'
        self.params = {
            'access_token': self.access_token,
            'v': self.version
        }
    def user_info(self, user_id):
        url = f'{self.base_url}users.get'
        params = {
            **self.params,
            'user_ids': user_id
        }
        response = requests.get(url, params=params)
        return response.json()
    
    def photo_info(self, user_id, count=5):
        url = f'{self.base_url}photos.get'
        params = {
            **self.params,
            'owner_id': user_id,
            'album_id': 'profile',
            'extended': 1,
            'count': count
        }
        response = requests.get(url, params=params).json() 
        items = response['response']['items']
        size_priority = {'w': 5, 'z': 4, 'y': 3, 'x': 2, 'm': 1, 's': 0}
        
        for item in items:
            likes_count = item.get('likes', {}).get('count', 0) 
            photo_sizes = item.get('sizes', []) 
            largest_photo = max(photo_sizes, key=lambda x: size_priority.get(x['type'], -1))
            largest_photo_url = largest_photo.get('url')  
            photo_date = item.get('date', 0)
            filename = f'{likes_count}_{photo_date}.jpg'
            pathfile = f'images/{filename}'
            image_response = requests.get(largest_photo_url)
            if image_response.status_code == 200:  # Проверяем успешность запроса
                with open(pathfile, 'wb') as f:
                    f.write(image_response.content)
            else:
                print(f'Не удалось скачать изображение')
            print(f'Likes: {likes_count}, Date: {photo_date}, Saved as: {pathfile}')
            
        return response  
        
class YAConnector:
    def __init__(self, token):
        self.headers = {'Authorization': f'OAuth {token}'}
    
    def create_folder(self, folder_name):
        response = requests.put(url='https://cloud-api.yandex.net/v1/disk/resources',
                                headers=self.headers,
                                params={'path': folder_name})
        return response.status_code
    
    def upload_2_folder(self, folder_name):
        directory = "images"
        files = os.listdir(directory)
        print(f"Files to upload: {files}")
        
        for filename in tqdm(files):
            local_file_path = os.path.join(directory, filename)
            url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
            params = {
                'path': f'{folder_name}/{filename}',  # Указываем путь на Яндекс.Диск
                'overwrite': 'true'  # Перезапись файлов
            }
            response = requests.get(url, params=params, headers=self.headers)
            upload_link = response.json().get('href')
            with open(local_file_path, 'rb') as f:
                response = requests.put(upload_link, files={'file': f})

  
connector = VKConnector(vk_token)
user_info = connector.user_info(246157421)
photo_info = connector.photo_info(246157421, 2)
#pprint(user_info)
yaconnector = YAConnector(ya_token)
yaconnector.create_folder('Backup')
yaconnector.upload_2_folder('Backup')
#pprint(yaconnector)
#pprint(photo_info)
#print(response.status_code)
