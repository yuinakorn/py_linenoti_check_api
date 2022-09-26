from datetime import datetime

from fastapi import FastAPI
import requests
import os
from dotenv import dotenv_values

config_env = {
    **dotenv_values(".env"),
    **os.environ,
}

app = FastAPI()


@app.get("/")
async def root():
    global error_hos, jdata
    url = config_env['URL1']

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    payload = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    json_data = response.json()
    error_hos = []
    i = 0
    e = 0
    for data in json_data:
        urls = f"{config_env['URL2']}{data['hcode']}"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        payload = {}
        try:
            response = requests.request("GET", urls, headers=headers, data=payload)
            json_data = response.json()

            # because of the source is different type of data
            if type(json_data) == dict:
                jdata = json_data['status']
            elif type(json_data) == list:
                jdata = json_data[0]['status']

            print(data['hcode'], " ", data['hname'], jdata)

            if jdata != 'OK':
                error_hos.append(f"{data['hcode']} {data['hname']} {jdata}")
                e += 1

        except Exception as err:
            print(err)
            pass

        i += 1

    error_hos.append(f"Total {i} hospital {e} error")

    str_trim = str(error_hos).replace('[', '').replace(']', '').replace("'", '').replace(",", '\n')
    str_trim = str("\n" + " " + str_trim)

    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    str_trim = str("\n" + " Report at " + now + str_trim)

    url = config_env['LINE_NOTIFY']

    payload = {"message": str(str_trim)}
    headers = {
        'Authorization': 'Bearer ' + config_env['LINE_TOKEN'],
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)

    # encode to utf-8
    return str_trim.encode('utf-8')
