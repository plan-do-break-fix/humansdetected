#!/bin/python3

import sqlite3
import os

SCHEMA = "CREATE TABLE IF NOT EXISTS manual_label ("\
         "  label TEXT NOT NULL"\
         ");"

def run():
    labels = sqlite3.connect("/home/user/Documents/labels-manual.humansdetected.sqlite3.db")
    c = labels.cursor()
    c.execute(SCHEMA)

    c.execute("SELECT COUNT(*) FROM manual_label")
    result = c.fetchone()
    count = result[0] + 1 if result else 1

    source = sqlite3.connect("/home/user/Documents/survey.humansdetected.sqlite3.db")
    src = source.cursor()
    src.execute("SELECT COUNT(*) FROM text")
    max_count = int(src.fetchone()[0])

    while count <= max_count:
        src.execute("SELECT * FROM text WHERE pk=?", count)
        result = src.fetchone()[0]
        os.system("clear")
        print(result[1])
        value = None
        while not value:
            inp = input("art, simple, delete: ")
            if inp == "a":
                value = "art"
            elif inp == "s":
                value = "simple"
            elif inp == "d":
                value = "delete"
        c.execute("INSERT INTO manual_label (label) VALUES (?)", (value,))
        labels.commit()
        count += 1