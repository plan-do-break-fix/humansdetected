#!/usr/bin/python3

"""
This script combines the data in the survey database with manual labels
and produces a normalized MySQL database for use in prodcution of the
Humans Detected web application.

"""

import mysql.connector
from os import environ
import sqlite3
from typing import Dict, List


from flask.app.DataConnect import Database, AwsConnect
from migrate import TxtParser as parser

FINAL = int(1000001)  # One million domains, two-indexed

class Bridge():

    def __init__(self, production, surveyDB=None, manualLabelDB=None):
        self.prod = production
        if surveyDB:
            self.srvy_conn = surveyDB
            self.srvy_c = self.srvy_conn.cursor()
        if manualLabelDB:
            self.lbl_conn = manualLabelDB
            self.lbl_c = self.lbl_conn.cursor()

    def process_core_migration(self, restart=885658) -> bool:
        # domain is selected from both tables and checked for equality
        #   when the duplicate domain name string is popped off the array.
        if restart:
            self.srvy_c.execute("SELECT domain, text FROM survey WHERE id > ?;", (str(restart),))
        else:
            restart = 0
            self.srvy_c.execute("SELECT domain, text FROM survey;")
        for count, (domain, htext) in enumerate(self.srvy_c):
            domainID = self.prod.insert_domain(domain)
            if htext:
                htextID = self.prod.insert_htext(htext)
                self.prod.relate_domain_to_htext(domainID, htextID)
            print(f"{str(restart+count+1)} | {domain} processed.")
            #input([domain, htext, flags, substrings, categorical])

    def process_label_migration(self, restart=False) -> bool:
        pass

    ################ BREAK APART INTO CORE MIGRATION AND PARSER DATA MIGRATION/CONTINUATION

    def process_row(self, domain: str,
                          htext: str,
                          flags: List[str],
                          substrings: List[str],
                          categorical: Dict[str, List[str]]
                          ) -> bool:
        domainID = self.prod.insert_domain(domain)
        htextID = self.prod.insert_htext(htext)
        self.prod.relate_domain_to_htext(domainID, htextID)
        #for lang in langs:
        #    langID = self.prod.getlangangaugeID(lang)
        #    if not langID:
        #        langID = self.prod.insert_language(lang)
        #    self.prod.relate_htext_to_language(htextID, langID)
        for flag in flags:
            flagID = self.prod.get_flagID(flag)
            if not flagID:
                flagID = self.prod.insert_flag(flag)
            self.prod.relate_htext_to_flag(htextID, flagID)
        for substring in substrings:
            substringID = self.prod.get_substringID(substring)
            if not substringID:
                substringID = self.prod.insert_substring(substring)
            self.prod.relate_htext_to_substring(htextID, substringID)
        for category in categorical.keys():
            categoryID = self.prod.get_categoryID(category)
            if not categoryID:
                categoryID = self.prod.insert_category(category)
                for substring in categorical[category]:
                    substringID = self.prod.get_substringID(substring)
                    if not substringID:
                        substringID = self.prod.insert_substring(substring)
                    self.prod.relate_htext_to_substring(htextID, substringID)
                    self.prod.relate_substring_to_category(substringID, categoryID)

            
def migrate():
    # check environment variables
    print("Calling migration method...")
    required_envars = ["SURVEY_SQLITE_PATH",
                       "RDS_HOSTNAME",
                       "RDS_PORT",
                       "RDS_DB_NAME",
                       "RDS_USERNAME",
                       "RDS_PASSWORD"]
    if not all([var in environ.keys() for var in required_envars]):
        raise ValueError
    # make database connections
    srvy_db = sqlite3.connect(environ["SURVEY_SQLITE_PATH"])
    #lbl_db = sqlite3.connect(environ["LABELS_SQLITE_PATH"])
    prod = Database.Interface(AwsConnect.get_rds_connection())
    # create and run bridge
    bridge = Bridge(prod, surveyDB=srvy_db)
    bridge.process_core_migration()






if __name__ == "__main__":
    print("Migration initiated")
    migrate()
