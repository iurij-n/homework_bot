from pprint import pprint
import requests

TOKEN = 'AQAAAAASWs4aAAYckVnFE8x9YEaii-cSMWqvmBo'
url = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
headers = {'Authorization': f'OAuth {TOKEN}'}
payload = {'from_date': 1639158976}

# Делаем GET-запрос к эндпоинту url с заголовком headers и параметрами params
homework_statuses = requests.get(url, headers=headers, params=payload)

# Печатаем ответ API в формате JSON
#print(homework_statuses.text)

# А можно ответ в формате JSON привести к типам данных Python и напечатать и его
pprint(homework_statuses.json())
# response = requests.get('https://www.swapi.tech/api/starships/9/')
# pprint(response.json())
#print(response.json().get('result').get('properties').get('name'))

if len(homework_statuses.json().get('homeworks')) != 0:
    print(homework_statuses.json().get('homeworks')[0].get('status'))