import os
import subprocess
import sys

if __name__ == '__main__':
    print("BEGIN ...")
    print("echo Create security.txt file with line .LOGON db14.cgs.uchi.ru/U,P")
    with open("tail_bteq.txt", "w") as fw:
        fw.write(".LOGOFF")
    sqlname = sys.argv[1].split("~")[0]
    logname = sys.argv[1].split("~")[1]

    print("BEGIN " + sqlname)
    with open("bteq.txt", "w") as fw:
        with open("security.txt") as fr:
            for line in fr.readlines():
                fw.write(line)
        with open(sqlname) as fr:
            for line in fr.readlines():
                fw.write(line)
        with open("tail_bteq.txt") as fr:
            for line in fr.readlines():
                fw.write(line)
    with open("run.txt", "w") as fw:
        fw.write(".Run File =bteq.txt\n")
    os.system("\"C:\\Program Files (x86)\\Teradata\\Client\\15.10\\bin\\bteq.exe\" <run.txt >log.txt 2>&1")

    with open(logname, "w") as fw:
        with open("log.txt") as fr:
            for line in fr.readlines():
                if "|" not in line and "-+-" not in line:
                    fw.write(line)
                else:
                    fw.write("#INFO DELETED BY SCRIPT#\n")
    print("END " + sqlname)
    print("... END")