#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint


#1.75 million rows of data!
osm_file = open("somerville-xml.osm")


# Regex
lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


def count_tags(filename):
    tags = {}

    for _, elem in ET.iterparse(filename):
        if elem.tag in tags:
            tags[elem.tag] += 1
        else:
            tags[elem.tag] = 1

    return tags


def count_keys(filename):
    keys = {}

    for _, elem in ET.iterparse(filename):
        if elem.tag == "tag":
            k = elem.get("k")
            if k in keys:
                keys[k] += 1
            else:
                keys[k] = 1

    return keys


def recursive_count_keys(filename):
    keys = {}

    for _, elem in ET.iterparse(filename):
        if elem.tag == "tag":
            k = elem.get("k")
            keys = recursive_tree(keys, k)

    return keys



#Source: http://stackoverflow.com/questions/354038/how-do-i-check-if-a-string-is-a-number-in-python
def is_int(s):
    if is_dict(s) or s is None:
        return False

    try:
        int(s)
        return True
    except ValueError:
        return False

def is_dict(d):
    if isinstance(d, dict):
        return True
    return False


tag = "address"

keys = {

}



def recursive_tree(keys, tag, first=True):
    # Handle pre-existing key
    if tag in keys:
        if first:
            #TODO: Cant assume this is an object could be a num
            keys[tag]["root"] += 1
            return keys
        else:
            keys[tag] += 1
            return keys            

    # Handle base case
    if len(split_keys(tag)) == 1:
        keys[tag] = 1
        return keys
    
    cur_key = split_keys(tag)[0] #address
    next_key = split_keys(tag)[1] #street

    # RIGHT NOW handles assumes all values are objects or nothing
    # Need to handle if value is an int
    cur_obj = keys.get(cur_key)

    # If cur_key exists and has a value of a number
    if is_int(cur_obj):
        val = keys[cur_key]
        next_obj = { cur_key : val }
    # If cur_key exists and has a value of a object
    elif cur_obj:
        next_obj = cur_obj
    # If cur_key does not exist
    else:
        next_obj = {}


    #Enter the jungle
    updated_keys = recursive_tree(next_obj, next_key, False)

    if updated_keys:
        keys[cur_key] = updated_keys
        return keys






def split_keys(key):
    return key.split(":", 1)


def count_keys_tree(filename):
    keys = {}

    for _, elem in ET.iterparse(filename):
        if elem.tag == "tag":
            k = elem.get("k")

            split_keys = k.split(":", 1)
            if len(split_keys) > 1:
                compound_key = split_keys[0] + "_compound"
                new_key = split_keys[1]
                if compound_key in keys:
                    if new_key in keys[compound_key]:
                        keys[compound_key][new_key] += 1
                    else:
                        keys[compound_key][new_key] = 1
                else:
                    keys[compound_key] = { new_key: 1 }
            else:
                if k in keys:
                    keys[k] += 1
                else:
                    keys[k] = 1
    return keys


def audit_key(attrib, element, keys):
    if element.tag == "tag":
        val = element.get(attrib)

        if re.search(problemchars, val):
            keys["problemchars"] += 1
        elif re.search(lower, val):
            keys["lower"] += 1
        elif re.search(lower_colon, val):
            keys["lower_colon"] += 1
        else:
            keys["other"] += 1

    return keys


def process_key_audit(filename, attrib):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    
    for _, element in ET.iterparse(filename):
        keys = audit_key(attrib, element, keys)

    return keys


if __name__ == '__main__':
    #v_validity_scores = process_map(osm_file, "v")
    #pprint.pprint(v_validity_scores)
    # results = count_keys_tree(osm_file)
    # pprint.pprint(results)
    #results = recursive_count_keys(osm_file)
    
    results = recursive_tree(keys, tag)
    pprint.pprint(results)
    



