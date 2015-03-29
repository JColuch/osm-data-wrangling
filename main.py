#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint
import json



# Regex
lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')



class OsmDescribe:

    def __init__(self, filename):
        self.osm_file = filename

        self.name = filename.split(".")[0]

        self.data_file = "audit_data_" + self.name + ".json" #TODO: name based on tag attr

        self.TC = TypeCheck()

    def count_elem_names(self, filename):
        """ Return dictionary; keys = element names, values = count of element """
        tags = {}

        for _, elem in ET.iterparse(filename):
            if elem.tag in tags:
                tags[elem.tag] += 1
            else:
                tags[elem.tag] = 1

        return tags


    def count_tag_attr(self, filename, tag_name):
        """  """
        attributes = {}

        for _, elem in ET.iterparse(filename):
            if elem.tag == tag_name:

                for item in elem.attrib:
                    if item in attributes:
                        attributes[item] += 1
                    else:
                        attributes[item] = 1

        return attributes


    def count_tag_attr_vals(self, filename, tag_name, attr_name):
        """ Return dictionary; keys = tag key names, values = count of key """

        keys = {}

        for _, elem in ET.iterparse(filename):
            if elem.tag == tag_name:
                attr = elem.get(attr_name)
                if attr in keys:
                    keys[attr] += 1
                else:
                    keys[attr] = 1

        return keys

    # DEPRECATED: Generalized via function: build_tag_attr_val_tree()
    # def count_tag_keys_tree(self, filename):
    #     """ Return dictionary; keys = tag key names, values = count of key """

    #     keys = {}

    #     for _, elem in ET.iterparse(filename):
    #         if elem.tag == "tag":
    #             k = elem.get("k")
    #             keys = parse_key(keys, k)

    #     return keys

    def get_tag_attr_val_tree(self, filename, tag_name, attr_name):

        keys = {}

        for _, elem in ET.iterparse(filename):
            if elem.tag == tag_name:
                attr = elem.get(attr_name)
                keys = self.parse_key(keys, attr)

        return keys


    def parse_key(self, keys, tag):
        """" Return keys object with parsed key """
        # Handle pre-existing key
        if tag in keys:
            if "root" not in keys[tag]:
                keys[tag] = { "root" : 1 }

            keys[tag]["root"] += 1

            return keys

        # Handle base case
        if len(self.split_keys(tag)) == 1:
            keys[tag] = { "root" : 1 }
            return keys
        
        cur_key = self.split_keys(tag)[0] #address
        next_key = self.split_keys(tag)[1] #street

        # Comment the code
        cur_obj = keys.get(cur_key)

        # If cur_key exists and has a value of a number
        if self.TC.is_int(cur_obj):
            val = keys[cur_key]
            next_obj = { cur_key : val }
        # If cur_key exists and has a value of a object
        elif cur_obj:
            next_obj = cur_obj
        # If cur_key does not exist
        else:
            next_obj = {}

        # Recursive call
        updated_keys = self.parse_key(next_obj, next_key)

        if updated_keys:
            keys[cur_key] = updated_keys
            return keys


    def split_keys(self, key):
        """ Returns list; splits string on colon """

        return key.split(":", 1)



class OsmAudit:

    def __init__(self):
        pass


    def audit_key(self, attrib, element, keys):
        """ Checks key against regex for validity"""

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



class Cleaner:

    def __init__(self):
        pass



class CleanerTools:

    def __init__(self):
        pass



class TypeCheck:

    def __init__(self):
        pass

    def is_int(self, s):
        """ Return True if variable is an int """

        if self.is_dict(s) or s is None:
            return False

        try:
            int(s)
            return True
        except ValueError:
            return False

    def is_dict(self, d):
        """ Return True if argument is a dictionary """

        if isinstance(d, dict):
            return True
        return False



tag = "service"

keys = {
    'address': {
        'root': 1,
        'apartment': {'root': 5},
        'street': {'root': 2}
        },
    'street': {'apartment': {'room': {'root': 1}}}}






#1.75 million rows of data!
osm_file = "somerville-xml.osm"


if __name__ == '__main__':

    tools = AuditTools()

    # #tags = tools.count_elem_names(osm_file)
    attrs = tools.count_tag_attr(osm_file, "nd")
    pprint.pprint(attrs)



    # data = tools.get_tag_attr_val_tree(osm_file, "nd", "ref")
    
    # with open("audit_data/audit.json", "w") as f_out:
    #     json.dump(data, f_out)
  
    



