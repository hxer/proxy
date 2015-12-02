#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""get some proxy ip
by haoxi, 2015.11.27
version:python2.7.x
*** TODO ***
[+]sqlite3支持的并发数有限，使用线程过多后，会出现超时，数据库locked现象
    [S]:减少线程数,更改默认超时时间,换其他数据库
"""

from __future__ import unicode_literals
import requests
from bs4 import BeautifulSoup
import Queue
import threading
import re
import logging
import os

from mimvpsql import MimvpSql

if False:
    import pytesseract
    from PIL import Image
    import io

logging.basicConfig(filename="proxy.log",
        level=logging.WARNING,
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M')

out_queue = Queue.Queue()
in_queue =  Queue.Queue()

class ThreadSql(threading.Thread):
    """
    """
    def __init__(self, in_queue):
        """
        """
        threading.Thread.__init__(self)
        self.in_queue = in_queue
        self.sql = MimvpSql()

    def run(self):
        """
        """
        while True:
            proxy = self.in_queue.get()
            result = self.sql.select_proxy(proxy[0])
            if result == -1:
                pass
            elif len(result):
                self.sql.update_proxy(proxy)
                print("MimvpSql proxy:Update successful")
                logging.info("MimvpSql proxy:Update successful")
            else:
                self.sql.insert_proxy(proxy)
                print("MimvpSql proxy:Insert successful")
                logging.info("MimvpSql proxy:Insert successful")
            self.in_queue.task_done()


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
        logging.warning("[!]not get proxy_msg, maybe web page change")
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
                    msg = [ table[p] for p in param ]
                    proxy_msg.append(msg)
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
                    logging.info("match 8080 port")
                    port = "8080"
                elif encrys == "4vMpAO0OO0O":
                    logging.info("match 80 port")
                    port = "80"
                else:
                    logging.info("not match encrys")
            else:
                logging.warning("[!]not match port, maybe web page change")
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
        return response.content
    except requests.exceptions.HTTPError as e:
        logging.error("[E]HTTP Error: %s", e)
        return None

def get_mimvp_urls():
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
        try:
            tags = soup.body.find("div", "tag_area")
            return [base_url+tag.attrs['href'] for tag in tags.find_all('a')]
        except Exception as e:
            logging.error("[E]not match proxy urls: %s", e)
    return None

def main():
    #spqwn a pool of threads, and pass them queue instance
    for i in range(2):
        mp = MimvpProxy(in_queue, out_queue)
        mp.setDaemon(True)
        mp.start()

    td_sql = ThreadSql(out_queue)
    td_sql.setDaemon(True)
    td_sql.start()

    #populate queue with the data
    urls = get_mimvp_urls()
    for url in urls:
        in_queue.put(url)

    #wait on the queue until everything has been processed
    in_queue.join()
    out_queue.join()
    backup_sql()
    print("it has been finished")

def backup_sql():
    """
    """
    bk_command="cp mimvp.sqlite3 mimvp.sqlite3.bk"
    if os.system(bk_command) == 0:
        logging.info("backup sql successful")
    else:
        logging.warning("backup sql failed")

if __name__ == "__main__":
    from apscheduler.schedulers.blocking import BlockingScheduler

    sched = BlockingScheduler()
    sched.add_job(main, "interval", hours=1)
    try:
        sched.start()
    except:
        sched.shutdown()
