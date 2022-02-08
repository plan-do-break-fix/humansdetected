import re
from typing import List

def prepare(text) -> List[str]:
    lines = [_l.strip() for _l in text.split("\n") if _l]
    return lines

def get_tag_wrapper(lines, position):
    candidates = []
    if position == "fronting":
        _regex = r"^(/|#|\*|-)+( (/|#|\*|-)+)? +"
    elif position == "tailing":
        _regex = r" +((/|#|\*|-)+ )?(/|#|\*|-)+$"
    for _l in lines:
        result = re.search(_regex, _l)
        if result:
            candidates.append(result.group())
    if not candidates:
        return ""
    elif len(set(candidates)) == 1:
        return candidates[0]
    else:
        counts = {_c: 0 for _c in list(set(candidates))}
        for _c in candidates:
            counts[_c] += 1
        counts = [(counts[_c], _c) for _c in counts.keys()]
        counts.sort()
        if counts[-1][0] > counts[-2][0]:
            return counts[-1][1]
        else:
            #print("Unable to resolve correct tag wrapper:")
            #print(f"{[_i[1] for _i in counts if _i[0] == counts[-1][0]]}")
            return False
            
def tag_wrappers(lines):
    fronting = get_tag_wrapper(lines, "fronting")
    tailing = get_tag_wrapper(lines, "tailing")
    return (fronting, tailing)

def strip_wrappers(line):
    wrappers = tag_wrappers([line])
    if not any(wrappers):
        return line
    elif all(wrappers):
        return line[len(wrappers[0]):0-len(wrappers[1])]

def strip_line_label(line):
    result = re.search(r"[aA-zZ ]+: +", line)
    if result:
        return line[len(result.group()):]
    return line
    
def section_titles(lines, tag_wrappers):
    lines = [_l for _l in lines
             if _l.startswith(tag_wrappers[0])
             and _l.endswith(tag_wrappers[1])]
    lines = [_l[len(tag_wrappers[0]):0-len(tag_wrappers[1])] for _l in lines]
    return [_l for _l in lines if _l]

def lines_by_section(lines, sections, tag_wrappers):
    output = {_s: [] for _s in sections}
    lns = {}
    for _s in sections:
        for _i, _l in enumerate(lines):
            if _l.startswith(tag_wrappers[0] + _s):
                lns[_s] = _i
    lns = [(lns[_s], _s) for _s in lns.keys()]
    lns.sort()
    for _i, _s in enumerate(lns):
        first_l = _s[0]
        if _i < len(lns) - 1:
            last_l = lns[_i+1][0]
        else:
            last_l = len(lns) - 1
        output[_s[1].lower()] = lines[first_l:last_l]
    return output

def labeled_technologies(lines_by_section):
    output, lines = [], None
    if "site" in lines_by_section.keys():
        lines = lines_by_section["site"]
    elif "technology colophon" in lines_by_section.keys():
        lines = lines_by_section["technology colophon"]
    if not lines:
        return False
    for _l in lines:
        items = [_i.strip() for _i in strip_line_label(_l).split(",")]
        for _i in items:
            if _i not in output:
                output.append(_i)
    return output