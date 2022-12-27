from fastapi import FastAPI, Form, HTTPException
import requests
import os
from dotenv import dotenv_values
from datetime import datetime, timezone, timedelta
import pymysql

connection = pymysql.connect(host='172.17.5.12',  # private ip (VPN)
                             user='ihims',
                             password='Admin_ssj#2022',
                             db='api',
                             charset='utf8mb4',
                             port=6034
                             )

config_env = {
    **dotenv_values(".env"),
    **os.environ,
}

app = FastAPI()


@app.get("/pi/noline/t/{token}")
async def check_manual(token: str = None):
    if token == config_env['TOKEN']:
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
            if data['hcode'] == '' or str(data['hcode'])[0] == '0':
                continue

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

                hcode = "'" + data['hcode'] + "'"
                status = "'" + jdata + "'"
                check_time = "'" + datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S") + "'"
                sql = "INSERT INTO client_status_log (hoscode, status, checktime) VALUES (%s, %s, %s)" % \
                             (hcode, status, check_time)
                with connection.cursor() as cursor:
                    cursor.execute(sql)
                    connection.commit()

            except Exception as err:
                print(err)
                pass

            i += 1

        error_hos.append(f"Total {i} hospital {e} error")

        return str(error_hos).encode('utf-8')

    else:
        raise HTTPException(status_code=404, detail="Token Invalid")


@app.post("/pi")
async def send_line(keys: str = Form()):
    if keys == config_env['API_KEY']:
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
            if data['hcode'] == '' or str(data['hcode'])[0] == '0':
                continue

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

                # insert result to database
                hcode = "'" + data['hcode'] + "'"
                status = "'" + jdata + "'"
                check_time = "'" + datetime.now(timezone(timedelta(hours=7))).strftime("%Y-%m-%d %H:%M:%S") + "'"
                sql = "INSERT INTO client_status_log (hoscode, status, checktime) VALUES (%s, %s, %s)" % \
                      (hcode, status, check_time)
                with connection.cursor() as cursor:
                    cursor.execute(sql)
                    connection.commit()
               # end insert

            except Exception as err:
                print(err)
                pass

            i += 1

        error_hos.append(f"Total {i} hospital {e} error")

        str_trim = str(error_hos).replace('[', '').replace(']', '').replace("'", '').replace(",", '\n')
        str_trim = str("\n" + " " + str_trim)

        # now = datetime.now().strftime("%d/%m/%Y %H:%M")
        # now = datetime.datetime.now(LOCAL_TIMEZONE).strftime("%d/%m/%Y %H:%M")
        tz = timezone(timedelta(hours=7))
        now = datetime.now(tz=tz).strftime("%d/%m/%Y %H:%M")
        str_trim = str("\n" + " Report at " + now + str_trim)

        url = config_env['LINE_NOTIFY']

        payload = {"message": str(str_trim)}
        headers = {
            'Authorization': 'Bearer ' + config_env['LINE_TOKEN'],
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        # call LINE Notify API
        requests.request("POST", url, headers=headers, data=payload)

        # print(response.text)
        return str(error_hos).encode('utf-8')

    else:
        return "Wrong API key"
