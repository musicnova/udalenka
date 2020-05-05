import datetime
import hashlib
import os
import shutil
import sys
import time

def calc_md5hash(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def check_secret(fname, secret_value):
    with open(fname, "r") as f:
        for line in f.readline():
            if secret_value in line:
                return True
    return False

def parse_cron(fname):
    res = {}
    with open(fname, "r") as f:
        for line in f.readlines():
            arr = line.split("\t")
            res[arr[-1]] = arr[0:-1]
    return res

def check_cron(ts, rule, delta_mins):
    ts0 = ts - datetime.timedelta(minutes=delta_mins)
    line = datetime.date.strftime(ts0, "%M/%H/%d/%m/%Y")
    cur = line.split("/")
    for i in range(len(cur)):
        if cur[i] != rule[i] and rule[i] != "*":
            return 0
    return 1

def send_alerts(fname, alerts):
    with open(fname, "r") as f:
        for line in f.readlines():
            for email in line.split(";"):
                for alert in alerts:
                    alpha = "alpha logs: https://stash.delta.uchi.ru/projects/BIGDATA/repos/sbx_ivanov/browse"
                    sigma = "sigma logs: https://sbtatlas.uchi.ru/stash/projects/BIGDATA/repos/sbx_ivanov/browse"
                    body = (alert + " " + alpha + " " + sigma).replace(' ', '%20')
                    url = ("mailto:?to="+email+"&subject=alert_sbx_ivanov&body="+body).replace('\n', '%20')
                    print(url)

def run():
    print("1. pull sql files")
    if os.path.isdir("scripts"): shutil.rmtree("scripts")
    os.system("git pull")

    print("2. check start script (hash sum or secret word)")
    start_script = "_start.py"
    print(start_script)
    md5_value = calc_md5hash(start_script)
    print(md5_value)
    secret_word = "please"
    print(secret_word)
    corrupted = "" != md5_value and not check_secret(start_script, secret_word)

    print("3. read schedule and make tasks")
    dict = parse_cron("_cron.txt")
    for k in dict.keys():
        print(dict[k])

    print("4. execute script for each task")
    ts = datetime.datetime.now()
    alerts = []
    for k in dict.keys():
        if sum([check_cron(ts, dict[k], i) for i in range(5)]) > 0:
            if corrupted:
                print("stop " + k)
                cmd = "python.exe" + start_script + " ERROR_" + k
                os.system(cmd)
            else:
                print("start " + k)
                cmd = "python.exe " + start_script + " " + k
                os.system(cmd)
            alerts.append(k)
        else:
            print("skip " + k)

    print("5. push log files to feature/predrelease")
    os.system("git add *.log")
    os.system("git commit -m \"feature/predrelease update after start\"")
    os.system("git push")

    print("6. process _mailto.txt")
    send_alerts("_mailto.txt", alerts)

    print("7. sleep 300 seconds and repeat")

if __name__ == '__main__':
    while True:
        run()
        time.sleep(300)