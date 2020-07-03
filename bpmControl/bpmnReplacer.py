#!/usr/bin/python3
import os
import argparse

def replacerFiles(file, slug, replacer):
    try:

        with open(file, 'r') as f:
            txt = f.read()

        with open(file, 'w') as f:
            new_txt = txt.replace("'%s'"%slug, "'%s'"%replacer)
            new_txt = txt.replace('"%s"'%slug, '"%s"'%replacer)
            f.write(new_txt)
            
        return True, None

    except Exception as err:
        return None, err


def searchFileInTxt(search, path):
    result = []
    for i in os.walk(path):
        p = i[0]
        files = i[2]
        for file in files:
            filePath = os.path.join(p, file)
            try:
                with open(filePath, 'r') as f:
                    txt = f.read()
                    if "'%s'"%search in txt or '"%s"'%search in txt:
                        result.append({"file": filePath, "search": search})

                        
            except Exception as err:
                print("Fatal read file : ", err, ": ", file)
                continue

    return result


def parsingInputDate(file):
    data = {}
    try:
        with open(file, 'r') as f:
            for line in f:
                l = line.split()
                data[l[1]] = l[2]
    except Exception as err:
        print("Ошибка чтения входного файла")

    return data

def main(file, path, exts, replacer):
    data = parsingInputDate(file)

    for search, replacerValue in data.items():

        print("=" * 80)
        print("Search : ", search)

        searchingFiles = searchFileInTxt(search, path)

        for res in searchingFiles:
            print("... found: ", res["file"])

            if replacer:
                resultReplace = replacerFiles(res["file"], search, replacerValue)
                if resultReplace[1] is not None:
                    print("... error replace : ", resultReplace[1])
                    continue
                print("... replace: ", res["file"])

    print("... tHe EnD! ...")





if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='--help')
    parser.add_argument('--file', type=str, required=True)
    parser.add_argument('--path', type=str, default=os.getcwd(), required=False)
    parser.add_argument('--exts', default = None, type=str)
    parser.add_argument('--replacer', default = False, type=bool)
    args = parser.parse_args()

    main(args.file, args.path, args.exts, args.replacer)