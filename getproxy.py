#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""get some proxy ip
by haoxi, 2015.11.27
version:python2.7.x
"""

from __future__ import unicode_literals
import requests
from bs4 import BeautifulSoup
import sqlite3
import Queue
import threading
import re

if False:
    import pytesseract
    from PIL import Image
    import io


out_queue = Queue.Queue()
in_queue =  Queue.Queue()

class MimvpSql(threading.Thread):
    """
    """
    def __init__(self, in_queue):
        """
        """
        threading.Thread.__init__(self)
        self.in_queue = in_queue
        self.creater_table()


    def run(self):
        """
        """
        print("MimvpSql run ...")
        while True:
            proxy = self.in_queue.get()
            result = self.select_proxy(proxy[0])
            if len(result):
                self.update_proxy(proxy)
                print("MimvpSql proxy:Update successful")
            else:
                self.insert_proxy(proxy)
                print("MimvpSql proxy:Insert successful")
            self.in_queue.task_done()

    def creater_table(self):
        """
        """
        conn = sqlite3.connect('mimvp.sqlite3')
        cur = conn.cursor()
        cur.execute('''CREATE TABLE if not exists proxy
            (   id integer primary key,
                ip text not null,
                port text not null,
                httpt_ype text not null,
                anonymous text,
                country text,
                isp text,
                ping_time text,
                transfer_time text,
                check_time text
            )'''
        )
        conn.commit()
        conn.close()

    def insert_proxy(self, proxy):
        """
        parameter:
            proxy[list]:
        """
        sql = '''INSERT INTO proxy(ip,port,httpt_ype,anonymous,country,isp,
            ping_time,transfer_time,check_time)  VALUES (?,?,?,?,?,?,?,?,?)'''
        self.execute_sql(sql, proxy)

    def select_proxy(self, ip):
        """
        parameter:
            ip[str]:
        """
        sql = "SELECT ip FROM proxy where ip=(?)"
        return self.execute_sql(sql, (ip,))

    def update_proxy(self, proxy):
        """
        parameter:
            proxy[list]
        """
        sql = '''UPDATE proxy SET ip=?,port=?,httpt_ype=?,anonymous=?,country=?,isp=?,
            ping_time=?,transfer_time=?,check_time=? where ip=?'''
        proxy.append(proxy[0])
        self.execute_sql(sql, proxy)

    def execute_sql(self, sql, values=None):
        """
        """
        conn = sqlite3.connect('mimvp.sqlite3')
        cur = conn.cursor()
        cur.execute(sql, values)
        #just sql query success,cur.fetchall return not empty list
        #other like update, insert, return empry list
        result = cur.fetchall()
        conn.commit()
        conn.close()
        return result



class MimvpProxy(threading.Thread):
    """
    """
    def __init__(self,in_queue, out_queue):
        """
        """
        threading.Thread.__init__(self)
        self.out_queue = out_queue
        self.in_queue = in_queue

    def run(self):
        """
        """
        print("MimvpProxy run ...")
        while True:
            url = self.in_queue.get()
            proxy_msg = self.get_proxymsg(url)
            if proxy_msg:
                for msg in proxy_msg:
                    self.out_queue.put(msg)
            self.in_queue.task_done()

    def get_proxymsg(self,url):
        """先解析表头，然后解析表格
        """
        content = get_page(url)
        if content:
            soup = BeautifulSoup(content, "lxml")
            thead = [tag.attrs['id'] for tag in soup.body.thead.find_all("th")]
            tag_tbs = soup.tbody.find_all("td")
            if thead and tag_tbs:
                return self.parse_td(thead, tag_tbs)
            else:
                print("no tag td in proxy table")
                #log
        else:
            print("get_proxy_msg:no content")
        return None

    def parse_td(self, thead, soup_tbs):
        """
        """
        proxy_msg = []
        table = dict()
        param = ['p_ip', 'p_port', 'p_type', 'p_anonymous','p_country',
            'p_isp','p_ping','p_transfer','p_checkdtime']

        for i in xrange(0, 20*len(thead), len(thead)):
	    table = table.fromkeys(param, None)
            for index, attr in enumerate(thead):
                if attr in ['p_port']:
                    table[attr] = self.parse_port(soup_tbs[i+index].img.attrs['src'])
                elif attr in ['p_ping','p_transfer']:
                    table[attr] = soup_tbs[i+index].attrs['title']
                else:
                    table[attr] = soup_tbs[i+index].text
            if table['p_port']:
                try:
                    msg = [ table[p] for p in param ]
                    proxy_msg.append(msg)
                except:
                    print(table)
        return proxy_msg

    def parse_port(self, src):
        """识别图片中的端口号,此方法还不太准确
        """
        if False:
            url = "http://proxy.mimvp.com/" + src
            content = get_page(url)
            if content:
                image = Image.open(io.BytesIO(content))
                text =  pytesseract.image_to_string(image)
                return text
            return None
        else:
            #match
            port = None
            match = re.search(r".*?port=\w{6}(.*)", src)
            if match:
                encrys = match.group(1).strip()
                if encrys == "4vMpDgw":
                    print("match 8080 port")
                    port = "8080"
                elif encrys == "4vMpAO0OO0O":
                    print("match 80 port")
                    port = "80"
                else:
                    print("not match encrys")
            else:
                print("not match port")
            return port



def get_page(url):
        """
        """
        session = requests.session()
        headers =  {
            "User-Agent": "Mozilla/5.0 (X11; Linux i686; rv:42.0) Gecko/20100101 Firefox/42.0",
            "Connection": "keep-alive",
        }
        try:
            response = session.get(url, headers=headers)
        except requests.exceptions.HTTPError:
            print("HTTP Error.")
            #log
            return None
        else:
            return response.content

def get_mimvp_purls():
    """get different proxy urls
        return:
            list[url,]
            None
    """
    base_url = "http://proxy.mimvp.com/"
    url = "http://proxy.mimvp.com/free.php"
    content = get_page(url)
    if content:
        soup = BeautifulSoup(content, "lxml")
        tags = soup.body.find("div", "tag_area")
        if tags:
            return [base_url+tag.attrs['href'] for tag in tags.find_all('a')]
        else:
            print("not match proxy urls")
            # log
    return None

def main():
    #spqwn a pool of threads, and pass them queue instance
    for i in range(1):
        mp = MimvpProxy(in_queue, out_queue)
        mp.setDaemon(True)
        mp.start()

    mp_sql = MimvpSql(out_queue)
    mp_sql.setDaemon(True)
    mp_sql.start()

    #populate queue with the data
    urls = get_mimvp_purls()
    for url in urls:
        in_queue.put(url)

    #wait on the queue until everything has been processed
    in_queue.join()
    out_queue.join()

if __name__ == "__main__":
    main()
    print("it has been finished")
