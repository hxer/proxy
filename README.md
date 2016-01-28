# getProxy

get some Proxy from web

# sqlite3 table and columns

'''
CREATE TABLE if not exists proxy
    (   id integer primary key,
        ip text not null,
        port text not null,
        http_type text not null,
        anonymous text,
        country text,
        isp text,
        ping_time text,
        transfer_time text,
        check_time text
    )
'''

# requirements

* htpwdScan

install

```
cd ~/ctf
git clone https://github.com/lijiejie/htpwdScan.git
cd htpwdScan
chmod u+x
sudo ln -s ~/ctf/htpwdScan/htpwdScan.py /usr/local/bin/htpwdscan    #cofirm htpwdScan.py begin with "#!/usr/bin/env python"
htpwdscan -h    # to run
```

* apscheduler

install

```
pip install apscheduler
```
