#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
by haoxi, 2015.12.2
version:python2.7.x
"""

from __future__ import unicode_literals
import sqlite3
import logging

class MimvpSql(object):
    """
    """
    def __init__(self):
        """
        """
        self.creater_table()

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
        try:
            conn = sqlite3.connect('mimvp.sqlite3')
            cur = conn.cursor()
            cur.execute(sql, values)
            #just sql query success,cur.fetchall return not empty list
            #other like update, insert, return empry list
            result = cur.fetchall()
            conn.commit()
            conn.close()
            return result
        except Exception as e:
            logging.error("database error: %s", e)
            return -1
