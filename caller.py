#!/Docker/py_linenoti_check_api/env/lib/ python3.10
# In the first line check your version python such as python3.10
import requests
import os
from dotenv import dotenv_values

config_env = {
    **dotenv_values(".env"),
    **os.environ,
}

url = config_env['API_URL']

# call the api but not wait for the response
try:
    requests.get(url, timeout=0.1)
except requests.exceptions.ReadTimeout:
    pass
