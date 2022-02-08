#!/bin/python3

import sqlite3
import os

SCHEMA = "CREATE TABLE IF NOT EXISTS manual_label ("\
         "  label TEXT NOT NULL"\
         ");"

def run():
    labels = sqlite3.connect("/home/user/Documents/humansdetected/humansdetected.manual_labels.sqlite3.db")
    c = labels.cursor()

    c.execute("SELECT text FROM label ORDER BY text DESC LIMIT(1);")
    previous = int(c.fetchone()[0])

    max_count = 549995

    while previous < max_count:
        previous += 1
        c.execute("SELECT * FROM text WHERE pk=?", (previous,))
        result = c.fetchone()
        os.system("clear")
        print(result[1])
        inp = input("(a)rt, (d)elete: ")
        if inp == "a":
            c.execute("INSERT INTO manual_label (label) VALUES ('art')")
        elif inp == "d":
            c.execute("INSERT INTO manual_label (label) VALUES ('delete')")
        if inp in ["a", "d"]:
            labels.commit()