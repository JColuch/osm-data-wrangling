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


def get_k_value_summary(filename):
    """Count all k values and number of variations of each."""
    data = count_elem_attr_vals(filename, "tag", "k")
    summary_data = {}

    for key in data:
        key_obj = data[key]
        count, variations = _update_key_count(key_obj)

        summary_data[key] = {"count": count, "variations": variations}

    return summary_data


def get_k_value_breakdown(filename):
    """Break down and count all key values, single and compound. Represent
    as nested dictionary data structure.
    """
    return count_elem_attr_vals(filename, "tag", "k")


def count_elem_attr_vals(filename, elem_name, attr_name):
    """Return dictionary; keys = tag key names, values = count of key """
    keys = {}

    for _, elem in ET.iterparse(filename):
        if elem.tag == elem_name:
            attr = elem.get(attr_name)
            keys = _add_key(keys, attr)

    return keys


def _update_key_count(obj, count=0, variations=0):
    """Recursively find and update count of key."""
    for key in obj:
        # Base Case
        if key == "root":
            count += obj[key]
            variations += 1
            continue

        new_obj = obj[key]
        count, variations = _update_key_count(new_obj, count, variations)

    return count, variations


def _add_key(keys, tag):
    """"Recursively parse key and add to keys dict."""
    # Recursive base case
    if len(_split_keys(tag)) == 1:
        if tag in keys:
            if "root" in keys[tag]:
                keys[tag]["root"] += 1
        else:
            keys[tag] = {"root": 1}

        return keys

    cur_key = _split_keys(tag)[0]
    next_key = _split_keys(tag)[1]

    # Get key value
    cur_obj = keys.get(cur_key)

    if cur_obj:
        next_obj = cur_obj
    else:
        next_obj = {}

    # Recursive call
    updated_keys = _add_key(next_obj, next_key)

    if updated_keys:
        keys[cur_key] = updated_keys
        return keys


def _split_keys(key):
    """Returns list; splits string on colon"""
    return key.split(":", 1)


if __name__ == '__main__':
    OSM_FILE = 'data/somerville-xml.osm'
    print get_k_value_breakdown(OSM_FILE)
