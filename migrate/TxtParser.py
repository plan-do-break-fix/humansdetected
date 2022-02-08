#!/usr/bin/python3
import re
from typing import Dict, List

from geotext import GeoText


def parse_flags(text: str) -> List[str]:
    output = []
    if is_google(text):
        output.append("google")
    elif is_craft_cms(text):
        output.append("craft_cms")
    elif is_zurb(text):
        output.append("zurb")
    elif is_robots(text):
        output.append("robot")
    return output
    
def parse_substrings(text: str) -> List[str]:
    output = []
    result = re.search(r"(?<![a-z])love", text.lower())
    if result:
        output.append("love")
    result = re.search(r"(?<![a-z])hate", text.lower())
    if result:
        output.append("hate")
    return output

def parse_substrings_by_category(text: str) -> Dict[str, List[str]]:
    return {"cities": GeoText(text).cities}


def is_google(text: str) -> bool:
    return True if text.startswith("Google is built by a large team of engineers, designers, "\
        "researchers, robots, and others in many different sites across the globe.") else False

def is_craft_cms(text: str) -> bool:
    return True if text.startswith("/* TEAM */\n\nCreator: Moz\nURL: https://moz.com\nDescription: "\
        "\n\n/* THANKS */\n\nCraftCMS - https://craftcms.com") else False

def is_zurb(text: str) -> bool:
    return True if text.startswith("/* Foundation was made by ZURB, an interaction design and "\
        "design strategy firm in Campbell, CA */") else False
    
def is_robots(text: str) -> bool:
    result = re.search(r"[Uu]ser-[Aa]gent", text[:120])
    return bool(result)