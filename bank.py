import requests

r = requests.post('http://127.0.0.1:8000/api/create_link_token')

print(r.json())