#!/usr/bin/env python

"""Module contains functions that analyze OSM XML elements of type tag.
"""

import re
import xml.etree.cElementTree as ET


LOWER = re.compile(r'^([a-z]|_)*$')
LOWER_COLON = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
PROBLEM_CHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


def validate_k_attributes(filename):
    """Analyze k values for valid names and count results."""
    keys = {"lower": 0, "lower_colon": 0, "problem_chars": 0, "other": 0}

    for _, element in ET.iterparse(filename):
        if element.tag == "tag":
            k_val = element.get("k")
            keys = _validate_key_type(keys, k_val)

    return keys


def _validate_key_type(keys, k_val):
    """Identify if k val contains invalid characters and count result."""
    if re.search(PROBLEM_CHARS, k_val):
        keys["problem_chars"] += 1
    elif re.search(LOWER, k_val):
        keys["lower"] += 1
    elif re.search(LOWER_COLON, k_val):
        keys["lower_colon"] += 1
    else:
        keys["other"] += 1

    return keys


if __name__ == '__main__':
    OSM_FILE = 'somerville-xml.osm'
    print validate_k_attributes(OSM_FILE)
