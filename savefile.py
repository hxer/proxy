# -*- coding:utf-8 -*-

import sqlite3
import subprocess
import os

sql_file = 'output/mimvp.sqlite3'
proxy_tmp_file = 'output/proxy_tmp.txt'
proxy_suc_file = 'output/001.proxy.servers.txt'

# save proxy ip and port to file from sqlite3 databse
conn = sqlite3.connect(sql_file)
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
            tf.write(line)

# checking, need htpwdScan.py(can download from github, then set shell command
# 'htpwdscan')
cmd = 'htpwdscan -u=www.baidu.com -proxylist={proxies} -checkproxy -suc="百度一下"'\
    .format(proxies=proxy_tmp_file)
s = subprocess.Popen(cmd, shell=True)
s.wait()
