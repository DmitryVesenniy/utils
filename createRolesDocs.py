# -*- coding: utf-8 -*-
#!/usr/bin/python3

import os
import json
import base64
import argparse

import requests

URL_DOC = "http://95.216.44.142/mdm/api/v1/nsi/dict/mgz_documentsTypes"
URL_APPROVE = "http://95.216.44.142/mdm/api/v1/nsi/dict/mgz_approval"
URL_ROLE = "http://95.216.44.142/mdm/api/v1/nsi/dict/mgz_project_roles"
URL_TYPE_APPROVE = "http://95.216.44.142/mdm/api/v1/nsi/dict/mgz_approvalType"
URL_CREATE_APPROVE = "http://95.216.44.142/mdm/api/v1/nsi/dict/save"

USER = "???????"
PASSWORD = "???????"

FIELDS = ("id", "code", "name", "approvalTypeCode")
FIELDS_KEY = ("documentType", "role", "listCode")
EXTS = ".conf"

class Approve:
    def __init__(self, approvalId, documentType, role, typeApprovalObj, deleted, listCode = None, order = None):
        self.id = approvalId
        self.documentObj = documentType
        self.roleObj = role
        self.typeApprovalObj = typeApprovalObj
        self.listCode = listCode
        self.order = order
        self.deleted = deleted

    def differences(self):
        pass

    def compare(self, codeApproveType):
        result = codeApproveType == self.typeApprovalObj["approvalTypeCode"] and self.deleted == 0

        if not result:
            self.differences()

        return result


def setHeadersAuth(user, passw):
    auth = "%s:%s"%(user, passw)
    return base64.b64encode(auth.encode("utf8")).decode("utf8")


def headersAuth():
    return { "Authorization" : "Basic %s"%setHeadersAuth( USER, PASSWORD ) }


def requestFromNsi(url, method, data = {}):
    respJson = None

    methods = {
        "GET": requests.get,
        "POST": requests.post,
        "PUT": requests.put
    }

    requestMethod = methods.get(method)
    if not requestMethod: return respJson, "Not methods"

    resp = requestMethod(url, headers = headersAuth(), data = data)
    if not resp.ok: return respJson, resp.status_code

    try:
        respJson = resp.json()
    except Exception as err:
        return resp, None

    return respJson, None


def genRequestFromNsi(url):

    respJson, err = requestFromNsi(url, "GET")
    if err: raise StopIteration

    for element in respJson["dict"]["elements"]:
        yield element


def getApproveNsi():
    result = {}

    for element in genRequestFromNsi(URL_APPROVE):
        idElement = element.get("id")
        deleted = element.get("deleted")
        if not idElement: continue

        # key dict
        keys = {}

        buff = {"approvalId": idElement}

        for elem in element["values"]:

            if isinstance(elem["valueAttr"], dict):
                buff[elem["nick"]] = {}

                valueId = elem["valueAttr"]["dict"]["elements"][0]["id"]
                buff[elem["nick"]]["id"] = valueId

                for value in elem["valueAttr"]["dict"]["elements"][0]["values"]:
                    if value["nick"] in FIELDS:
                        buff[elem["nick"]][value["nick"]] = value["valueAttr"]

                        # Ищем уникальные значения из которых будет состоять ключь
                        if elem["nick"] in FIELDS_KEY and value["nick"] == "code":
                            keys[elem["nick"]] = value["valueAttr"]
            else:
                buff[elem["nick"]] = elem["valueAttr"]
                if elem["nick"] in FIELDS_KEY:
                    keys[elem["nick"]] = elem["valueAttr"]

        if len(keys) < 2: continue


        result[" ".join([keys[i] for i in FIELDS_KEY if keys.get(i)])] = Approve(buff["approvalId"], buff["documentType"], buff["role"], 
            buff["type"], deleted, buff.get("listCode"), buff.get("order"))

    return result


def getDataNsi(url):
    result = {}

    for element in genRequestFromNsi(url):
        idElement = element.get("id")
        key = None
        name = None

        for i in element["values"]:

            if i["nick"] == "code":
                key = i.get('valueAttr')
                continue
            if i["nick"] == "name":
                name = i.get('valueAttr')
                break
        if key and idElement:
            result[key] = {"name": name, "id": idElement}

    return result


def getRequestTypeApproveFromNsi():
    result = {}

    for element in genRequestFromNsi(URL_TYPE_APPROVE):
        idElement = element["id"]
        key = None
        duration = None

        for i in element["values"]:

            if i["nick"] == "approvalTypeCode":
                key = i['valueAttr']
                continue

            if i["nick"] == "approvalDuration":
                duration = i['valueAttr']
                continue

        if key:
            result[key] = {"id": idElement, "duration": duration}

    return result


def parserConfigFile(file_path):
    """
    struct File {

        //Структура файла:
        listCode string
        documentType[,documentType*] string
        role,type[,approveBy] []string

    }
    """
    roleArgs = ("role", "type", "approveBy")
    configApprove = {
        "listCode": '',
        "documents": [],
        "roles": [],
    }
    indexBehavior = 0

    try:
        with open(file_path, 'r') as f:
            txt = f.read()
    except Exception as err:
        return (None, err)

    lines = txt.split('\n')

    for line in lines:
        line = line.strip()

        if indexBehavior == 0:
            configApprove["listCode"] = line
            indexBehavior += 1
            continue

        if line and line.startswith("MGZ_DOC"):
            configApprove["documents"] += list(map(lambda x: x.strip(), lines[1].split(',')))
            continue
        
        if line and line.startswith("MGZ_BPM"):
            role = {}

            for i, value in enumerate(map(lambda x: x.strip(), line.split(','))):
                try:
                    role[roleArgs[i]] = value
                except (IndexError, ValueError, TypeError):
                    continue

            configApprove["roles"].append(role)

    return (configApprove, None)


def createNsiApproval(documentTypeID, roleId, typeId, orderValue, listCode = None):
    """
    data = {
        "ValueDict":{
            "NickDict": "mgz_approval", 
            "Element":{
                "Deleted": 0, 
                "ElementParent": None, 
                "Values": [
                    {"Deleted": 0, "LinkValue": {"Id": "26bc06cf-b52b-45a9-9344-efbc36d11fb7"}, "NickAttr": "documentType"},
                    {"Deleted": 0, "LinkValue": {"Id": "f9ea6c54-da00-4f60-bb74-4fde559f162a"}, "NickAttr": "role"},
                    {"Deleted": 0, "LinkValue": {"Id": "31f3fab7-388c-42af-b705-9cc48f3368a3"}, "NickAttr": "type"}, #assent PT4H
                    {"Deleted": 0, "Value": 1000, "NickAttr": "order"},
                    {"Deleted": 0, "Value": "assent", "NickAttr": "listCode"},
                ]
            }
        }
    }
    """
    data = {
        "ValueDict":{
            "NickDict": "mgz_approval", 
            "Element":{
                "Deleted": 0, 
                "ElementParent": None, 
                "Values": [
                    {"Deleted": 0, "LinkValue": {"Id": documentTypeID}, "NickAttr": "documentType"},
                    {"Deleted": 0, "LinkValue": {"Id": roleId}, "NickAttr": "role"},
                    {"Deleted": 0, "LinkValue": {"Id": typeId}, "NickAttr": "type"}, #assent PT4H
                    {"Deleted": 0, "Value": orderValue, "NickAttr": "order"},
                ]
            }
        }
    }
    if listCode:
        data["ValueDict"]["Element"]["Values"].append({"Deleted": 0, "Value": listCode, "NickAttr": "listCode"})

    resp, err = requestFromNsi(URL_CREATE_APPROVE, "POST", data = json.dumps(data))

    if err: return False

    if resp.ok:
        return True

    return False


def main(path):
    roles = getDataNsi(URL_ROLE)
    documents = getDataNsi(URL_DOC)
    approvesType = getRequestTypeApproveFromNsi()
    approvesNsi = getApproveNsi()

    order = 1

    for file in os.listdir(path):
        if not file.endswith(EXTS): continue

        conf, err = parserConfigFile(os.path.join(path, file))
        if err: 
            print("Error parsing file: %s, error: %s"%(file, err))
            continue

        listCode = conf["listCode"]

        for document in conf["documents"]:

            for role in conf["roles"]:
                key = " ".join([i for i in [document, role["role"], listCode] if i])

                if key in approvesNsi and approvesNsi[key].compare(role["type"]): continue
                try:
                    documentId = documents[document]["id"]
                    roleId = roles[role["role"]]["id"]
                    approveTypeId = approvesType[role["type"]]["id"]
                except Exception as err:
                    print("Error data arguments : ", err)
                    continue

                resp = createNsiApproval(documentId, roleId, approveTypeId, order, listCode)

                if resp:
                    print("** Save approve -> ", key)
                    order += 1
                else:
                    print("** Error Save approve -> ", key)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='--help')
    parser.add_argument('--path', type=str, required=True)
    parser.add_argument('--exts', default = None, type=str)
    args = parser.parse_args()

    if args.exts:
        EXTS = args.exts

    main(args.path)
