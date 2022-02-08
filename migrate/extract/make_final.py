#!/bin/python3
import sqlite3


SCHEMAS = [
    "CREATE TABLE IF NOT EXISTS master ("\
    "  pk INTEGER NOT NULL PRIMARY KEY,"\
    "  domain TEXT NOT NULL,"\
    "  text INTEGER NULL,"\
    "  FOREIGN KEY (text) REFERENCES text (pk)"\
    ");",
    "CREATE TABLE IF NOT EXISTS text ("\
    "  pk INTEGER NOT NULL PRIMARY KEY,"\
    "  text TEXT NOT NULL"\
    ");",
    "CREATE TABLE IF NOT EXISTS label ("\
    "  text INTEGER NOT NULL,"\
    "  ascii_art INTEGER NULL,"\
    "  empty_template INTEGER NULL,"\
    "  for_robots INTEGER NULL,"\
    "  FOREIGN KEY (text) REFERENCES text (pk)"\
    ");"
]
#    "CREATE TABLE IF NOT EXISTS metric ("
#    "  n_char INTEGER NOT NULL,"
#    "  n_line INTEGER NOT NULL,"

def run():
    w_conn = sqlite3.connect("/home/user/Documents/humansdetected.sqlite3.db")
    w = w_conn.cursor()
    for schema in SCHEMAS:
        w.execute(schema)
    w_conn.commit()
    r_conn = sqlite3.connect("/home/user/Documents/survey.humansdetected.sqlite3.db")
    r = r_conn.cursor()
    lbl_conn = sqlite3.connect("/home/user/Documents/labels-manual.humansdetected.sqlite3.db")
    lbl = lbl_conn.cursor()

    #w.execute("SELECT COUNT(*) FROM master")
    #last_entered = int(w.fetchone()[0])

    #r.execute("SELECT * FROM master_list WHERE pk > ?", (last_entered,))
    #for _i in r:
    #    w.execute("INSERT INTO master (pk, domain) VALUES (?, ?)",
    #              (_i[0], _i[1]))
    #    w_conn.commit()
    r.execute("SELECT * FROM text")
    for _i in r:
        lbl.execute("SELECT label FROM manual_label WHERE rowid=?", (_i[0],))
        label = lbl.fetchone()[0]
        if label in ["art", "simple"]:
            w.execute("INSERT INTO text (pk, text) VALUES (?, ?)", (_i[0], _i[2]))
            w.execute("UPDATE master SET text=? WHERE domain=?", (_i[0], _i[1]))
            if label == "art":
                w.execute("INSERT INTO label (text, ascii_art) VALUES (?, ?)", (_i[0], 1))
            w_conn.commit()
    r_conn.close()
        

