from datetime import datetime
import mysql.connector
from mysql.connector import errorcode
from os import environ
from random import randint
from typing import List, Union

from time import sleep


SCHEMA = (
    "TABLE 'domains' ("
    "  'id' MEDIUMINT UNSIGNED NOT_NULL AUTO_INCREMENT,"
    "  'domain' CHAR(255) NOT_NULL,"
    "  'accessed' CHAR(19),"
    "  'status' TINYINT UNSIGNED DEFAULT NULL,"
    "  'content_type' ENUM("
    "    'html',"
    "    'txt',"
    "    'xml'"
    "    ),"
    "  'content' VARCHAR(8000) DEFAULT NULL,"
    "  'error' ENUM("
    "    'connection',"  # BaseHTTPError, ConnectionError, HTTPError, InvalidURL, RequestException, RetryError, SSLError
    "    'content',"     # ContentDecodingError | UnicodeDecodeError, UnicodeError
    "    'redirect',"    # TooManyRedirects
    "    'timeout'"      # ConnectTimeout, ReadTimeout, Timeout
    "    )"
    ");"
)


class MySqlInterface:

    def __init__(self, logger):
        self.log = logger
        self.signature = randint(1000000000,9999999999)
        self.conn = mysql.connector.connect(
            user=environ["DB_USER"],
            password=environ["DB_PASSWD"],
            host=environ["DB_HOST"]
        )
        self.c = self.conn.cursor()
        self.c.execute("USE humans;")

    def return_unaccessed_domain(self) -> str:
        self.c.execute("SELECT domain FROM domains"
                       "  WHERE accessed IS NULL"
                       "  LIMIT 1;")
        result = self.c.fetchone()
        if not result:
            raise RuntimeError
        domain = result[0]
        self.c.execute("UPDATE domains"
                       "  SET"
                       "    accessed = IF(accessed IS NULL, %s, accessed)"
                       "  WHERE domain = %s;",
                       (self.signature, domain))
        self.conn.commit()
        self.c.execute("SELECT accessed FROM domains"
                       "  WHERE domain = %s;",
                       (domain,))
        result = self.c.fetchone()
        owner = int(result[0])
        if owner != self.signature:
            return self.return_unaccessed_domain()
        return domain
        
    def domain_exists(self, domain) -> Union[int, bool]:
        self.c.execute("SELECT id FROM domains WHERE domain = %s;", (domain,))
        result = self.c.fetchone()
        return result[0] if result else False

    def add_domain(self, domain) -> int:
        """Add a domain to the database and returns the primary key."""
        self.c.execute("INSERT INTO domains (domain) VALUES (%s);", (domain,))
        self.conn.commit()
        return self.c.lastrowid

    def record_result(self, domain, timestamp, status, content_type, content):
        """Updates the database with the results of a search then checks in the domain."""
        self.c.execute("UPDATE domains"
                       "  SET"
                       "    accessed = %s,"
                       "    status = %s,"
                       "    content_type = %s,"
                       "    content = %s"
                       "  WHERE domain = %s;",
                       (timestamp, status, content_type, content, domain))
        self.conn.commit()
        
    def record_error(self, domain, timestamp, error):
        """Updates the database with a search error then checks in the domain."""
        self.c.execute("UPDATE domains"
                       "  SET"
                       "    status = 0,"
                       "    accessed = %s,"
                       "    error = %s"
                       "  WHERE domain = %s;",
                       (timestamp, error, domain))
        self.conn.commit()


def load_domains() -> List:
    import csv
    db = MySqlInterface()
    with open(f"./majestic_million.csv") as _f:
        lines = csv.reader(_f, delimiter=",")
        for line in lines:
            db.add_domain(line[2])