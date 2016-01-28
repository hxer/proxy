# -*- coding:utf-8 -*-

import sqlite3
import subprocess
import os

proxy_tmp_file = 'proxy_tmp.txt'
proxy_suc_file = 'proxy_suc.txt'

# save proxy ip and port to file from sqlite3 databse
conn = sqlite3.connect('mimvp.sqlite3')
cur = conn.cursor()
cur.execute('select ip,port from proxy where http_type=?', ('HTTP',))
with open(proxy_tmp_file, 'w') as f:
    for row in cur.fetchall():
        line = "{ip}:{port}\n".format(ip=row[0].strip(), port=row[1].strip())
        f.write(line)

# add had checked proxy file to proxy_tmp_file for checking again
if os.path.exists(proxy_suc_file):
    with open(proxy_tmp_file, 'a') as tf, open(proxy_suc_file) as sf:
        for line in sf.read():
            proxy_tmp_file.write(line)

# checking, need htpwdScan.py(can download from github, then set shell command
# 'htpwdscan')
cmd = 'htpwdscan -u=www.baidu.com -proxylist=proxy.txt -checkproxy -suc="百度一下" \
    -o={f}'.format(f=proxy_suc_file)
s = subprocess.Popen(cmd, shell=True)
s.wait()
