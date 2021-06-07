import csv
from datetime import datetime
import logging
import requests
from requests.exceptions import *
from typing import List

import mysql.connector
from mysql.connector import errorcode

from MySqlInterface import MySqlInterface

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36",
           "Upgrade-Insecure-Requests": "1",
           "DNT": "1",
           "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
           "Accept-Language": "en-US,en;q=0.5",
           "Accept-Encoding": "gzip, deflate"}


class Agent:

    def __init__(self, data_path="."):
        self.setup_logger()
        self.db = MySqlInterface(self.log)
        self.log.info(f"Agent initialized.")

    def setup_logger(self) -> None:
        logger = logging.getLogger("HumanDetector")
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s [%(name)s] %(levelname)-8s %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        self.log = logger

    def run(self) -> None:
        while True:
            domain = self.db.return_unaccessed_domain()
            if not domain:
                raise RuntimeError
            self.search(domain)

    def search(self, domain) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        self.log.debug(f"Checking {domain}.")
        resp = self.fetch(domain)
        if not resp:
            return None
        self.log.debug(f"{domain} response status {resp.status_code}.")
        if not 199 < resp.status_code < 300:
            self.db.record_result(domain, timestamp, resp.status_code, None, None)
        content = resp.content.decode()
        content_type = self.content_type(content)
        if content_type in ["html", "xml"]:
            self.log.info(f"Bogus content at {domain}.")
            content = None
        elif content_type == "txt":
            self.log.info(f"Humans found at {domain}.")
        self.db.record_result(domain, timestamp, resp.status_code, content_type, content)

    def fetch(self, domain) -> requests.Response:
        timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        try:
            resp = requests.get(f"http://{domain}/humans.txt", headers=HEADERS, timeout=(10,10))
            return resp
        except (BaseHTTPError, ConnectionError, HTTPError, InvalidURL, RequestException, RetryError, SSLError):
            self.log.error(f"Connection error at {domain}.")
            self.db.record_error(domain, timestamp, "connection")
        except (ConnectTimeout, ReadTimeout, Timeout):
            self.log.error(f"Timeout error at {domain}.")
            self.db.record_error(domain, timestamp, "timeout")
        except TooManyRedirects:
            self.log.error(f"Redirect error at {domain}.")
            self.db.record_error(domain, timestamp, "redirect")
        except (ContentDecodingError, UnicodeDecodeError, UnicodeError):
            self.log.error(f"Content error at {domain}.")
            self.db.record_error(domain, timestamp, "content")
        return False

    def content_type(self, content):
        content = content[:50] if len(content) > 50 else content
        content = content.strip().upper()
        if "<!DOCTYPE HTML" in content or "<HTML" in content:
            return "html"
        elif "<?XML" in content:
            return "xml"
        return "txt"


if __name__ == "__main__":
    app = Agent()
    app.run()
