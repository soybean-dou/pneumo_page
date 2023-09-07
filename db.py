#!/usr/bin/python

import sqlite3
import datetime as dt
import os
import sys
from pathlib import Path

def insert_user(user_info):
    conn = sqlite3.connect(str("pneumo_service.db"))
    c = conn.cursor()
    query=f"SELECT user_key FROM user WHERE user_key = '{user_info['user_key']}'"
    c.execute(query)
    num=c.fetchall()
    if(len(num)==0):
        x=dt.datetime.now()
        date=x.strftime("%A %d. %B %Y %H:%M:%S")
        query=f"INSERT INTO user VALUES ('{user_info['user_key']}', '{user_info['email']}', '{user_info['name']}', '{date}')"
        print("insert new user")
        c.execute(query)
        if not(os.path.exists("./user/"+user_info['user_key'])):
            os.system("mkdir ./user/"+user_info['user_key'])
            print("make ./user/"+user_info['user_key'])
        conn.commit()
        conn.close()


def insert_job(user_info,job_info):
    state="queue"
    conn = sqlite3.connect(str("pneumo_service.db"))
    c = conn.cursor()
    c.execute(f"SELECT * FROM job WHERE user_key='{user_info['user_key']}'")
    num=c.fetchall()
    job_num=len(num)+1
    x=dt.datetime.now()
    date=x.strftime("%A %d. %B %Y %H:%M:%S")
    c.executemany('INSERT INTO jobs VALUES (?,?, ?, ?, ?, ?,?,?)',
                  [(user_info["user_key"],user_info["username"],job_num,job_info["jobname"],job_info["file1"],state,date)])
    conn.commit()
    conn.close()

def read_db(user_key):
    conn = sqlite3.connect(str("pneumo_service.db"))
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute(f"SELECT * FROM job WHERE user_key ='{user_key}'")
    tb=c.fetchall()
    return tb

def update_db(user_key,key,state):
    conn = sqlite3.connect(str("pneumo_service.db"))
    c = conn.cursor()
    c.execute("UPDATE job SET state = ? WHERE id = ?",(state,key))
    conn.commit()
    conn.close()

def read_db_row(username,key):
    conn = sqlite3.connect(str("./user/userjob.db"))
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM jobs WHERE id == "+str(key))
    tb=c.fetchall()
    cols = [column[0] for column in c.description]
    return tb, cols
