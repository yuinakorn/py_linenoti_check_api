import requests

url = ""

# call the api but not wait for the response
try:
    requests.get(url, timeout=0.1)
except requests.exceptions.ReadTimeout:
    pass


