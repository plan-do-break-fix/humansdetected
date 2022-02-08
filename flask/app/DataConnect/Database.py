#!/usr/bin/python3

"""
This script combines the data in the survey database with manual labels
and produces a normalized MySQL database for use in prodcution of the
Humans Detected web application.

"""

SCHEMA = (
    "'domain' ("
    "  'id' MEDIUMINT UNSIGNED PRIMARY KEY,"
    "  'domain' CHAR(255) UNIQUE NOT_NULL,"
    "  INDEX (domain)"
    ");",
    "'htext' ("
    "  'id' MEDIUMINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,"
    "  'text' VARCHAR(8000) UNIQUE NOT_NULL,"
    "  INDEX (text)"
    ");",
    #"'language' ("
    #"  'id' TINYINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,"
    #"  'language' CHAR(3) UNIQUE NOT_NULL",
    #");",
    "'flag' ("
    "  'id' SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,"
    "  'flag' CHAR(128) NOT_NULL"
    ");",
    "'substring' ("
    "  'id' SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,"
    "  'substring' TINYTEXT NOT_NULL"
    ");",
    "'category' ("
    "  'id' SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,"
    "  'category' TINYTEXT NOT_NULL"
    ");",
    "'domain_htext' ("
    "  'id' MEDIUMINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,"
    "  'domain' MEDIUMINT UNSIGNED NOT_NULL,"
    "  'htext' MEDIUMINT UNSIGNED UNIQUE NOT_NULL,"
    "  FOREIGN KEY (domain)"
    "    REFERENCES domain(id)"
    "    ON DELETE CASCADE,"
    "  FOREIGN KEY (htext)"
    "    REFERENCES htext(id)"
    "    ON DELETE CASCADE"
    ");",
    "'htext_language' ("
    "  'id' MEDIUMINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,"
    "  'htext' MEDIUMINT UNSIGNED,"
    "  'language' TINYINT UNSIGNED,"
    "  FOREIGN KEY (htext)"
    "    REFERENCES htext(id)"
    "    ON DELETE CASCADE,"
    "  FOREIGN KEY (language)"
    "    REFERENCES languages(id)"
    "    ON DELETE CASCADE"
    ");",
    "'htext_flag' ("
    "  'id' MEDIUMINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,"
    "  'htext' MEDIUMINT NOT_NULL,"
    "  'flag' SMALLINT UNSIGNED NOT_NULL,"
    "  FOREIGN KEY (htext)"
    "    REFERENCES htext(id)"
    "    ON DELETE CASCADE,"
    "  FOREIGN KEY (flag)"
    "    REFERENCES flags(id)"
    "    ON DELETE CASCADE"
    ");",
    "'htext_substring' ("
    "  'id' MEDIUMINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,"
    "  'htext' MEDIUMINT NOT_NULL,"
    "  'substring' SMALLINT UNSIGNED NOT_NULL,"
    "  FOREIGN KEY (htext)"
    "    REFERENCES htext(id)"
    "    ON DELETE CASCADE,"
    "  FOREIGN KEY (substing)"
    "    REFERENCES substring(id)"
    "    ON DELETE CASCADE"
    ");",
    "'substring_category' ("
    "  'id' MEDIUMINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,"
    "  'substring' SMALLINT UNSIGNED NOT_NULL,"
    "  'category' SMALLINT UNSIGNED NOT_NULL,"
    "  FOREIGN KEY (substring)"
    "    REFERENCES substring(id)"
    "    ON DELETE CASCADE,"
    "  FOREIGN KEY (category)"
    "    REFERENCES category(id)"
    "    ON DELETE CASCADE"
    ");",
    "'parserRecord' ("
    "  'id' SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,"
    "  'parser' VARCHAR(64) NOT_NULL,"
    "  'lastText' MEDIUMINT UNSIGNED DEFAULT 0"
    ");",
    "'featureParameters' ("
    "  'id' SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,"
    "  'key' CHAR(128) NOT_NULL,"
    "  'value' MEDIUMINT UNSIGNED NOT_NULL"
    ");"

)


from os import environ
from typing import List, Union


class Interface:

    def __init__(self, database, create=False):
        self.conn = database
        self.c = self.conn.cursor()
        if create:
            self.create()

    def create(self):
        for definition in SCHEMA:
            cmd = f"CREATE TABLE IF NOT EXISTS {definition}"
            self.c.execute(cmd)
        self.conn.commit()

    # Insert into data tables
    def insert_domain(self, domain: str) -> int:
        if self.get_domainID(domain):
            return self.get_domainID(domain)
        self.c.execute("INSERT INTO domain (domain) VALUES (%s);", (domain,))
        self.conn.commit()
        self.c.execute("SELECT LAST_INSERT_ID();")
        return self.c.fetchone()[0]

    def insert_htext(self, text: str) -> int:
        if self.get_htextID(text):
            return self.get_htextID(text)
        self.c.execute("INSERT INTO htext (text) VALUES (%s);", (text,))
        self.conn.commit()
        self.c.execute("SELECT LAST_INSERT_ID();")
        return self.c.fetchone()[0]

    # Insert into lookup tables
    def insert_language(self, lang: str) -> int:
        if len(lang) != 3:
            raise ValueError("ISO 3166-1 language code must be three characters.")
        self.c.execute("INSERT IGNORE INTO language (language) VALUES (%s);", (lang,))
        self.conn.commit()
        self.c.execute("SELECT id FROM language WHERE langauge = %s;", (lang,))
        return self.c.fetchone()[0]

    def insert_flag(self, flag: str) -> int:
        self.c.execute("INSERT IGNORE INTO flag (flag) VALUES (%s);", (flag,))
        self.conn.commit()
        self.c.execute("SELECT id FROM flag WHERE flag = %s;", (flag,))
        return self.c.fetchone()[0]

    def insert_substring(self, substring: str) -> int:
        if not substring:
            raise ValueError("Substring must not be null or empty.")
        self.c.execute("INSERT IGNORE INTO substring (substring) VALUES (%s);", (substring,))
        self.conn.commit()
        self.c.execute("SELECT id FROM substring WHERE substring = %s;", (substring,))
        return self.c.fetchone()[0]

    def insert_category(self, category: str) -> int:
        self.c.execute("INSERT IGNORE INTO category (category) VALUES (%s);", (category,))
        self.conn.commit()
        self.c.execute("SELECT id FROM category WHERE category = %s;", (category,))
        return self.c.fetchone()[0]

    # Insert into relation tables
    def relate_domain_to_htext(self, domain: int, htext: int) -> bool:
        self.c.execute("SELECT id FROM domain_htext WHERE domain = %s and htext = %s;", (domain, htext))
        if self.c.fetchone():
            return True
        self.c.execute("INSERT IGNORE INTO domain_htext"
                       "  (domain, htext) VALUES (%s, %s);",
                       (domain, htext)) 
        self.conn.commit()
        return True

    def relate_htext_to_flag(self, htext: int, flag: int) -> bool:
        self.c.execute("SELECT id FROM htext_flag WHERE htext = %s and flag = %s;", (htext, flag))
        if self.c.fetchone():
            return True
        self.c.execute("INSERT IGNORE INTO htext_flag"
                       "  (htext, flag) VALUES (%s, %s);",
                       (htext, flag)) 
        self.conn.commit()
        return True

    def relate_htext_to_substring(self, htext: int, substring: int) -> bool:
        self.c.execute("SELECT id FROM htext_substring WHERE htext = %s and substring = %s;", (htext, substring))
        if self.c.fetchone():
            return True
        self.c.execute("INSERT IGNORE INTO htext_substring"
                       "  (htext, substring) VALUES (%s, %s);",
                       (htext, substring))
        self.conn.commit()
        return True

    def relate_substring_to_category(self, substring: int, category: int) -> bool:
        self.c.execute("SELECT id FROM substring_category WHERE substring = %s and category = %s;", (substring, category))
        if self.c.fetchone():
            return True
        self.c.execute("INSERT IGNORE INTO substring_category"
                       "  (substring, category) VALUES (%s, %s);",
                       (substring, category))
        self.conn.commit()
        return True

    # Value getters
    def get_domain(self, pk: int) -> str:
        self.c.execute("SELECT domain FROM domain WHERE id = %s;", (pk,))
        result = self.c.fetchone()
        return result[0] if result else ""

    def get_htext(self, pk: int) -> str:
        self.c.execute("SELECT htext FROM htext WHERE id = %s;", (pk,))
        result = self.c.fetchone()
        return result[0] if result else ""

    def get_language(self, pk: int) -> str:
        self.c.execute("SELECT language FROM language WHERE id = %s;", (pk,))
        result = self.c.fetchone()
        return result[0] if result else ""

    def get_flag(self, pk: int) -> str:
        self.c.execute("SELECT flag FROM flag WHERE id = %s;", (pk,))
        result = self.c.fetchone()
        return result[0] if result else ""

    def get_substring(self, pk: int) -> str:
        self.c.execute("SELECT substring FROM substring WHERE id = %s;", (pk,))
        result = self.c.fetchone()
        return result[0] if result else ""

    def get_category(self, pk: int) -> str:
        self.c.execute("SELECT category FROM category WHERE id = %s;", (pk,))
        result = self.c.fetchone()
        return result[0] if result else ""

    # ID (PK) getters
    def get_domainID(self, domain: str) -> int:
        self.c.execute("SELECT id FROM domain WHERE domain = %s;", (domain,))
        result = self.c.fetchone()
        return result[0] if result else 0

    def get_htextID(self, htext: str) -> int:
        self.c.execute("SELECT id FROM htext WHERE text = %s;", (htext,))
        result = self.c.fetchone()
        return result[0] if result else 0

    def get_langaugeID(self, langauge: str) -> int:
        self.c.execute("SELECT id FROM langauge WHERE langauge = %s;", (langauge,))
        result = self.c.fetchone()
        return result[0] if result else 0

    def get_flagID(self, flag: str) -> int:
        self.c.execute("SELECT id FROM flag WHERE flag = %s;", (flag,))
        result = self.c.fetchone()
        return result[0] if result else 0

    def get_substringID(self, substring: str) -> int:
        self.c.execute("SELECT id FROM substring WHERE substring = %s;", (substring,))
        result = self.c.fetchone()
        return result[0] if result else 0

    def get_categoryID(self, category: str) -> int:
        self.c.execute("SELECT id FROM category WHERE category = %s;", (category,))
        result = self.c.fetchone()
        return result[0] if result else 0

    def get_htextID_by_domain(self, domain: int) -> int:
        self.c.execute("SELECT htext FROM domain_htext WHERE domain = %s;", (domain,))
        result = self.c.fetchone()
        return result[0] if result else 0

    def get_htext_languageIDs(self, htext: int) -> List[int]:
        self.c.execute("SELECT lang FROM htext_language WHERE htext = %s;", (htext,))
        return self.c.fetchall()

    def get_htext_flagIDs(self, htext: int) -> List[int]:
        self.c.execute("SELECT flag FROM htext_flag WHERE htext = %s;", (htext,))
        return self.c.fetchall()

    def get_substring_categoryIDs(self, substring: int) -> List[int]:
        self.c.execute("SELECT category FROM substring_category WHERE substring = %s;", (substring,))
        return self.c.fetchall()

    def get_htextIDs_by_flag(self, flag: int) -> List[int]:
        self.c.execute("SELECT htext FROM htext_flag WHERE flag = '%s';", (flag,))
        return self.c.fetchall()

    def get_htextIDs_by_language(self, lang: int) -> List[int]:
        self.c.execute("SELECT htext FROM htext_language WHERE language = '%s';", (lang,))
        return self.c.fetchall()

    def get_htextIDs_by_substring(self, substring: int) -> List[int]:
        self.c.execute("SELECT htext FROM htext_substring WHERE substring = '%s';", (substring,))
        return self.c.fetchall()

    def get_substrings_by_category(self, category: int) -> List[int]:
        self.c.execute("SELECT substring FROM substring_category WHERE category = %s;", (category,))
        return self.c.fetchall()
    
    # Counters
    def count_domains(self) -> int:
        self.c.execute("SELECT COUNT(id) FROM domain;")
        result = self.c.fetchone()
        return result[0] if result else 0 

    def count_htexts(self) -> int:
        self.c.execute("SELECT COUNT(id) FROM htext;")
        result = self.c.fetchone()
        return result[0] if result else 0 

    def count_htexts_by_flag(self, flag: int) -> int:
        self.c.execute("SELECT COUNT(id) FROM htext_flag WHERE flag = %s;", (flag,))
        result = self.c.fetchone()
        return result[0] if result else 0 

    def count_htexts_by_substring(self, substring: int) -> int:
        self.c.execute("SELECT COUNT(id) FROM htext_substring WHERE substring = %s;", (substring,))
        result = self.c.fetchone()
        return result[0] if result else 0 

    # HText getters
    def get_htexts_by_flag(self, flag: int) -> List[int]:
        self.c.execute("SELECT id FROM htext_flag WHERE flag = '%s';", (flag,))
        return self.c.fetchall()

    def get_htexts_by_substring(self, substring: int) -> List[int]:
        self.c.execute("SELECT id FROM htext_substring WHERE substring = '%s';", (substring,))
        return self.c.fetchall()

    # Parser records
    def get_parserID(self, parser: str) -> int:
        self.c.execute("SELECT id FROM parserRecord WHERE parser = %s;", (parser,))
        result = self.c.fetchone()
        if not result:
            self.c.execute("INSERT INTO parserRecord (parser, lastText) VALUES (%s, %s);",
                           (parser, 0))
            self.conn.commit()
            self.c.execute("SELECT LAST_INSERT_ID();")
            result = self.c.fetchone()
        return result[0]

    def set_last_text(self, parser: int, htext_pk: int) -> bool:
        self.c.execute("UPDATE parser_record SET lastText = %s WHERE parser = %s;", (htext_pk, parser))
        self.conn.commit()
        return True

    def get_last_text(self, parser: int) -> int:
        self.c.execute("SELECT lastText FROM parserRecord WHERE id = %s;", (parser, ))
        return self.c.fetchone()[0]

    # Feature parameter methods
    """
    The feature parameter table enable use of batch-updated values in website features
        - Eliminates costly DB searches for webpage load
        - Does not include the most central or the most dynamic parameters:
          - Number humans.txt found
          - Number websites surveyed

    Feature parameter dictionary:
    {
        "google_count": int,
        "art_count": int,
        "craftcms_count": int,
        "zurb_count": int,
        "love_count": int,
        "hate_count": int,
        "robots_count": int,
        "shortest_pk": int,
        "shortest_length": int,
        "longest_pk": int,
        "longest_length": int,
        "city1_pk": int,
        "city1_count": int,
        "city2_pk": int,
        "city2_count": int,
        "city3_pk": int,
        "city3_count": int
    }

    """

    def get_paramID(self, key: str) -> int:
        self.c.execute("SELECT id FROM featureParameters WHERE key = %s;", (key,))

    def get_feature_params(self):
        self.c.execute("SELECT key, value FROM featureParameters;")
        return {row[0]: row[1] for row in self.c.fetchall()}

    def get_feature_param(self, key: str) -> int:
        self.c.execute("SELECT value FROM featureParameters WHERE key = %s;", (key,))
        return self.c.fetchone()[0]
                
    def set_feature_param(self, paramID: int, value: int) -> bool:
        self.c.execute("UPDATE featureParameters SET value = %s WHERE id = %s;",
                       (value, paramID))
        self.conn.commit()
        return True

    def update_feature_counts(self) -> bool:
        google_count = self.count_htexts_by_flag(self.get_flagID("google"))
        art_count = self.count_htexts_by_flag(self.get_flagID("art"))
        craftcms_count = self.count_htexts_by_flag(self.get_flagID("craftcms"))
        zurb_count = self.count_htexts_by_flag(self.get_flagID("zurb"))
        robots_count = self.count_htexts_by_flag(self.get_flagID("robots"))


    def update_cities(self) -> bool:
        category = self.get_categoryID("city")
        cities = self.get_substrings_by_category(category)
        counts = [[self.count_htexts_by_substring(city), city] for city in cities]
        counts.sort()
        city1_pk = counts[0][1]
        city1_count = counts[0][0]
        city2_pk = counts[1][1]
        city2_count = counts[1][0]
        city3_pk = counts[2][1]
        city3_count = counts[2][0]

    # update longest and shortest handled directly by Parser Agent

