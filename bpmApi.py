#!/usr/bin/python3
import base64
import argparse

import requests

URL_GET = "http://95.216.44.142:8085/app/mgz/bpm/repository/process-definitions?size=99999&key=%s"
URL_DELETE = "http://95.216.44.142:8085/app/mgz/bpm/repository/deployments/%s"

USER = "???????"
PASSWORD = "???????"


def setHeadersAuth(user, passw):
    auth = "%s:%s"%(user, passw)
    return base64.b64encode(auth.encode("utf8")).decode("utf8")

def headersAuth():
    return { "Authorization" : "Basic %s"%setHeadersAuth( USER, PASSWORD ) }


def get_bpm_process(bpm_id):
    resp = requests.get( URL_GET % bpm_id, headers = headersAuth() )
    if not resp.ok:
        print("Error connect server api, response code : ", resp.status_code)
        return {}

    return resp.json()


def delete_bpm_process(deploymentId):
    resp = requests.delete(URL_DELETE % deploymentId, headers = headersAuth())
    if resp.ok:
        print("-- Deleted process : ", deploymentId)
        return

    print("-- No deleted process : ", deploymentId)


def main(bpm_id):
    data = get_bpm_process(bpm_id)

    if not data.get("data"): 
        print("!!! Not data in response")

    for bpm in data["data"]:

        try:
            deploymentId = bpm['deploymentId']
            delete_bpm_process(deploymentId)

        except Exception as err:
            print(" ** Error main in :", err)
            continue
    print("THe EnD!!!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='--help')
    parser.add_argument('--bpm', type=str, required=True)
    args = parser.parse_args()

    main(args.bpm)
