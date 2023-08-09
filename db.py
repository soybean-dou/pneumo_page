#!/usr/bin/python

import sqlite3
import datetime as dt
import os
import sys
from pathlib import Path


def make_db(db_name):
    conn = sqlite3.connect(str("./user/userjob.db"))
    c = conn.cursor()
    c.execute('CREATE TABLE user_table(id INTEGER, username TEXT, jobname TEXT, input TEXT, type TEXT, state TEXT, date TEXT)')
    conn.commit()
    conn.close()

def insert_db(db_name,job_info):
    state="queue"
    conn = sqlite3.connect(str("./user/userjob.db"))
    c = conn.cursor()
    c.execute("SELECT * FROM user_table")
    num=c.fetchall()
    key_val=len(num)+1
    x=dt.datetime.now()
    date=x.strftime("%A %d. %B %Y %H:%M:%S")
    c.executemany('INSERT INTO user_table VALUES (?,?, ?, ?, ?, ?,?)',
                  [(key_val,job_info["username"],job_info["jobname"],job_info["filename"],job_info["wgstype"],state,date)])
    conn.commit()
    conn.close()

def read_db(username):
    conn = sqlite3.connect(str("./user/userjob.db"))
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM user_table WHERE username=?",(username))
    tb=c.fetchall()
    return tb

def update_db(username,key,state):
    conn = sqlite3.connect(str("./user/userjob.db"))
    c = conn.cursor()
    c.execute("UPDATE user_table SET state = ? WHERE id = ?",(state,key))
    conn.commit()
    conn.close()

def read_db_row(username,key):
    conn = sqlite3.connect(str("./user/userjob.db"))
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM user_table WHERE id == "+str(key))
    tb=c.fetchall()
    cols = [column[0] for column in c.description]
    return tb, cols
