#!/usr/bin/python3

import os
import argparse

def replacerFiles(path, search, exts = None, replacer = "", funcValue = None):
    if funcValue:
        func = lambda x: True if x in funcValue else False
    else:
        func = lambda x: True
    for i in os.walk(path):
        p = i[0]
        files = i[2]
        for file in files:
            if exts and not file.endswith(exts): continue
            try:
                with open(os.path.join(p, file), 'r') as f:
                    txt = f.read()
                    if search in txt:
                        print(">> ", os.path.join(p, file))
                if replacer and func(txt):
                    with open(os.path.join(p, file), 'w') as f:
                        new_txt = txt.replace(search, replacer)
                        f.write(new_txt)
                        print("-- reolacing : ", file)
            except Exception as err:
                print("Fatal read file : ", err, ": ", file)
                continue


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='--help')
    parser.add_argument('--path', type=str, default=os.getcwd(), required=False)
    parser.add_argument('--search', type=str, required=True)
    parser.add_argument('--exts', default = None, type=str)
    parser.add_argument('--replacer', default = "", type=str)
    parser.add_argument('--funcValue', default = None, type=str)
    args = parser.parse_args()

    replacerFiles(args.path, args.search, args.exts, args.replacer, args.funcValue)