#!/usr/bin/python

import sqlite3
import datetime as dt
import os
import sys
from pathlib import Path

def insert_user(user_info):
    conn = sqlite3.connect(str("pneumo_service.db"))
    c = conn.cursor()
    query=f"SELECT google_id FROM user WHERE google_id = '{user_info['google_id']}'"
    c.execute(query)
    num=c.fetchall()
    if(len(num)==0):
        x=dt.datetime.now()
        date=x.strftime("%A %d. %B %Y %H:%M:%S")
        query=f"INSERT INTO user VALUES ('{user_info['sub']}', '{user_info['google_id']}', '{user_info['email']}', '{user_info['name']}', '{date}')"
        print("insert new user")
        c.execute(query)
        if not(os.path.exists("./user/"+user_info['google_id'])):
            os.system("mkdir ./user/"+user_info['google_id'])
            print("make ./user/"+user_info['google_id'])
        conn.commit()
        conn.close()


def insert_job(user_info,job_info):
    state="queue"
    conn = sqlite3.connect(str("pneumo_service.db"))
    c = conn.cursor()
    c.execute("SELECT * FROM job")
    num=c.fetchall()
    job_num=len(num)+1
    x=dt.datetime.now()
    date=x.strftime("%A %d. %B %Y %H:%M:%S")
    c.executemany('INSERT INTO user_table VALUES (?,?, ?, ?, ?, ?,?)',
                  [(user_info["google_id"],user_info["name"],job_num,job_info["jobname"],job_info["filename"],job_info["wgstype"],state,date)])
    conn.commit()
    conn.close()

def read_db(user_id):
    conn = sqlite3.connect(str("pneumo_service.db"))
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM jobs WHERE google_id =?",(user_id))
    tb=c.fetchall()
    return tb

def update_db(username,key,state):
    conn = sqlite3.connect(str("./user/userjob.db"))
    c = conn.cursor()
    c.execute("UPDATE job SET state = ? WHERE id = ?",(state,key))
    conn.commit()
    conn.close()

def read_db_row(username,key):
    conn = sqlite3.connect(str("./user/userjob.db"))
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM job WHERE id == "+str(key))
    tb=c.fetchall()
    cols = [column[0] for column in c.description]
    return tb, cols
