# -*- coding: utf-8 -*-
#!/usr/bin/python3

import os
import re
import argparse

patternScripts = re.compile(r'<script>(.*?)</script>', re.DOTALL)
patternDoc = re.compile(r'.*def documentType\s*=\s*\'(.*?)\'.*', re.DOTALL)
patternDocs = re.compile(r'.*def documentTypes\s*=\s*\[(.*?)\].*', re.DOTALL)
patternListCode = re.compile(r'.*listCode\s*=\s*\'(.*?)\'.*', re.DOTALL)
patternMetaDateBpmn = re.compile(r'<documentation>(.+?)</documentation>', re.DOTALL)

PATH_RESULT = "conf"
EXTS = ".txt"

def getDocFromScripts(scripts):

    for script in scripts:
        documentTypes = patternDocs.findall(script)
        documentType = patternDoc.findall(script)
        listCode = patternListCode.findall(script)
        yield documentType, documentTypes, listCode


def getScripts(txt):
    scripts = []

    scriptsbpm = patternScripts.findall(txt)

    for script in scriptsbpm:
        if "calcApprovalListExt" in script:
            scripts.append(script)

    return scripts


def generateFile(path, metaDocument, data):
    
    if not os.path.isdir(path):
        os.mkdir(path)

    file_name = " ".join([metaDocument] + data["documents"] + [data["listCode"]])
    file_name = file_name.strip() + EXTS

    if os.path.isfile(os.path.join(path, file_name)): return '\033[96m%s\033[0m'%( "!! there is " + file_name), None

    try:

        with open(os.path.join(path, file_name), 'w', encoding='utf8') as f:
            f.write("{0}\n".format(data["listCode"]))
            f.write("{0}\n".format(",".join(data["documents"])))
    except Exception as err:
        return False, str(err)

    return file_name, None


def formationData(data):
    result = {}

    result["listCode"] = data[2][0]
    result["documents"] = []

    if len(data[0]) > 0:
        result["documents"].append(data[0][0])

    if len(data[1]) > 0:
        result["documents"] += list(map(lambda x: x.strip(' ').strip("'"), data[1][0].split(',')))

    return result


def main(path, outpath):
        
    for file in os.listdir(path):
        filePath = os.path.join(path, file)
        if not file.endswith(".bpmn") or not os.path.isfile(filePath): continue

        try:
            with open(filePath, 'r', encoding='utf8') as f:
                bpmnXml = f.read()

        except Exception as err:
            print("Error read file: <%s>, err: %s"%(file, err))
            continue

        metaDocument = patternMetaDateBpmn.findall(bpmnXml)[0].split(" ")[0]

        scripts = getScripts(bpmnXml)

        for data in getDocFromScripts(scripts):
            if not any(data[:2]):
                print("\033[91m%s\033[0m"%"** Есть признаки согласования но нет данных : ")
                print("\033[91m  ---%s\033[0m"%file)
                continue

            dataFormatted = formationData(data)
            result, err = generateFile(outpath, metaDocument, dataFormatted)
            if err:
                print("** Error write file: <%s>, err: %s"%(file, err))
                continue

            print("** OK!!. Create file: <%s> to: <%s>"%(file, result))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='--help')
    parser.add_argument('--path', type=str, required = True)
    parser.add_argument('--outpath', type=str, required = True)
    args = parser.parse_args()

    main(args.path,args.outpath)