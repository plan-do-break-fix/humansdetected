import csv
from datetime import date
import logging
import requests
import sqlite3
from typing import List

from requests.exceptions import ConnectionError, ContentDecodingError, ReadTimeout, Timeout, TooManyRedirects

SCHEMA = "CREATE TABLE IF NOT EXISTS 'domains' ("
         "  domain TEXT NOT NULL,"
         "  status INTEGER DEFAULT NULL,"
         "  accessed TEXT DEFAULT NULL,"
         "  content TEXT DEFAULT NULL"
         ");"

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36",
           "Upgrade-Insecure-Requests": "1",
           "DNT": "1",
           "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
           "Accept-Language": "en-US,en;q=0.5",
           "Accept-Encoding": "gzip, deflate"}


class Finder:

    def __init__(self, data_path="."):
        self.setup_logger()
        self.conn = sqlite3.connect(f"{data_path}/search-records.sqlite3.db")
        self.c = self.conn.cursor()
        self.c.execute(SCHEMA)
        self.conn.commit()

    def setup_logger(self) -> None:
        logger = logging.getLogger("HumanFinder")
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s [%(name)s] %(levelname)-8s %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        self.log = logger

    def run(self) -> None:
        run = True
        while run:
            domain = self.get_domain()
            if not domain:
                run = False
                break
            self.search(domain)
            
    def get_domain(self) -> str:
        self.c.execute("SELECT domain FROM domains WHERE status IS NULL LIMIT 1")
        result = self.c.fetchone()
        return result[0] if result else False


    def load_domains(self) -> List:
        with open(f"./majestic_million.csv") as _f:
            lines = csv.reader(_f, delimiter=",")
            for line in lines:
                self.add_domain(line[2])

    def search(self, domain) -> None:
        try:
            resp = requests.get(f"http://{domain}/humans.txt", headers=HEADERS, timeout=(5, 25))
            if not str(resp.status_code).startswith("2"):
                content = None
            else:
                self.log.debug(f"Humans found at {domain}!")
                content = resp.content.decode()
            self.record_search(domain, resp.status_code, content)
        except ConnectionError:
            self.record_search(domain, 0, "ConnectionError")
            return None
        except (ReadTimeout, Timeout):
            self.record_search(domain, 0, "Timeout")
            return None
        except TooManyRedirects:
            self.record_search(domain, 0, "TooManyRedirects")
            return None
        except (UnicodeDecodeError, UnicodeError):
            self.record_search(domain, 0, "UnicodeError")
            return None
        except ContentDecodingError:
            self.record_search(domain, 0, "ContentDecodingError")
            return None

    def add_domain(self, domain) -> bool:
        self.c.execute("INSERT INTO domains (domain) VALUES (?)", (domain,))
        self.conn.commit()

    def record_search(self, domain, status, content=None) -> bool:
        datestr = date.today().strftime("%Y-%m-%d")
        self.c.execute("UPDATE domains SET status=?, accessed=?, content=? "\
                       "WHERE domain=?", (status, datestr, content, domain))
        self.conn.commit()
        return True

    def domain_exists(self, domain) -> bool:
        self.c.execute("SELECT rowid FROM domains WHERE domain=?", (domain,))
        return bool(self.c.fetchone())
