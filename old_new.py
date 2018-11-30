#!/usr/local/python2.7/bin/python
# -*- coding: utf-8 -*-

'''
OLD ID to NEW ID
'''
import os, sys

def main():
    '''
    開始点
    '''

    params_len = len(sys.argv)

    if len(sys.argv) != 4:
        print("usage:")
        print("   python old_new.py <table file> <src file> <new file>")
        sys.exit(1)

    table_file = sys.argv[1]
    old_new = {}
    if os.path.exists(table_file) is True:
        table = open(table_file, "r")
        lines = table.read().split("\n")
        for aline in lines:
            if aline == "":
                continue
            #print("%s -> %s"%(aline.split()[0],aline.split()[1]))
            old_new[aline.split()[0]] = aline.split()[1]

        table.close()

    infilename = sys.argv[2]
    outfilename = sys.argv[3]

    if os.path.exists(infilename) is True:
        infile = open(infilename, "r")
    else:
        sys.exit(1)

    outfile = open(outfilename, "w")

    inlines = infile.read()
    for item in old_new:
        print("old = %s to new = %s"%(item, old_new[item]))
        inlines = inlines.replace(item, old_new[item])

    outfile.write(inlines)

    infile.close()
    outfile.close()

if __name__ == '__main__':
    main()

