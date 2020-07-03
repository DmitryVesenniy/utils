# -*- coding: utf-8 -*-
#!/usr/bin/python3

import os
import re
import argparse

activitiPattern = re.compile(r'\s*<activiti:formProperty (.*?)>\s*</activiti:formProperty>\s*', re.DOTALL)
valuePattern = re.compile(r'\s*id="(.*?)"\s*', re.DOTALL)

def createSetChars():
    alfabet = "qwertyuiopasdfghjklzxcvbnm_"
    alfabet = alfabet + alfabet.upper()
    return set(map(lambda x: ord(x), list(alfabet)))


ALFABET = createSetChars()


def getDocuments(file_bpmn):
    documents = []

    try:
        with open(file, 'r') as f:
            bmn_txt = f.read()

    except Exception as err:
        print("Ошибка чтения файла : ", file_bpmn)
        return None, err

    formProperty = activitiPattern.findall(bmn_txt)

    for form in formProperty:
        val = valuePattern.findall(form)
        if len(val) > 0 and val[0].startswith("doc_"):
            documents.append(val[0].strip())
            
    return documents, None


def searchcirillic(textList):
    cirillickName = {}

    for txt in textList:
        for ch in txt:
            if ord(ch) not in ALFABET:
                cirillickName.setdefault(txt, []).append(ch)

    return cirillickName


def main(path):
    result = {}

    for file in os.listdir(path):
        if not os.path.isfile(file) or not file.endswith(".bpmn"): continue

        formDocuments, _ = getDocuments(os.path.join(path, file))

        if not formDocuments:
            print("Not documents: ", file)
            continue

        searching = searchcirillic(formDocuments)

        if len(searching.keys()) > 0:
            result[file] = searching

    print("result: ", result)