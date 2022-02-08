#!/bin/python3
import mysql.connector
from mysql.connector import errorcode
import re
import sqlite3
from typing import Tuple

SCHEMA = [
    "CREATE TABLE IF NOT EXISTS master_list ("
    "  pk INTEGER NOT NULL PRIMARY KEY,"
    "  domain TEXT NOT NULL"
    ");",
    "CREATE TABLE IF NOT EXISTS text ("
    "  pk INTEGER NOT NULL PRIMARY KEY,"
    "  domain TEXT NOT NULL,"
    "  text TEXT NOT NULL"
    ");"
]

def extract(cursor, pk: int) -> Tuple:
    cursor.execute("SELECT domain, status, content_type, content"
                   "  FROM domains"
                   "  WHERE id = %s",
                   (pk,))
    return cursor.fetchone()

def good_text(text):
    if not text or type(text) != str:
        return False
    text = text.strip()
    if (len(text) < 8 or
          ("404 not found" in text.lower().split("\n")[0] 
           or "forbidden" in text.lower().split("\n")[0]
           or "does not exist" in text.lower().split("\n")[0]
           or "account suspended" in text.lower().split("\n")[0]
           or text.lower().startswith("error"))
        or
          (text.startswith("<") and not text.startswith("<<"))): # << is never a tag
        return False
    return True

def make_locals(db_path, mysql_host, user=None, passwd=None, _i=1, _f=500000):
    sqlite_conn = sqlite3.connect(db_path)
    sqlite_c = sqlite_conn.cursor()
    for schema in SCHEMA:
        sqlite_c.execute(schema)
    mysql_conn = mysql.connector.connect(
            user=user,
            password=passwd,
            host=mysql_host)
    mysql_c = mysql_conn.cursor()
    mysql_c.execute("USE humans;")
    while _i <= _f:
        data = extract(mysql_c, _i)
        sqlite_c.execute("INSERT INTO master_list (domain) VALUES (?)", (data[0],))
        status, content_type = data[1], data[2]
        if status == 200 and content_type == "txt" and good_text(data[3]):
            sqlite_c.execute("INSERT INTO text (text, domain) VALUES (?,?)", (data[3], data[0]))
        print(f"{_i} | {data[0]}/humans.txt")
        sqlite_conn.commit()
        _i += 1