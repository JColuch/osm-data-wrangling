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
        self.TC = TypeCheck()

    def describe_elements(self):
        print "Working...\n"

        data = self.count_elem_names(self.osm_file)

        self.fancy_print("describe_elements", data)

        return None

    def describe_element_attributes(self, elem_name):
        print "Working...\n"

        data = self.count_elem_attr(self.osm_file, elem_name)

        self.fancy_print("describe_element_attributes", data, [elem_name])

        return None

    def describe_element_attribute_values(self, elem_name, attr_name):
        print "Working...\n"

        data = self.count_elem_attr_vals(self.osm_file, elem_name, attr_name)

        self.fancy_print("describe_element_attribute_values", data,
                         [elem_name, attr_name])

        return None

    def fancy_print(self, fn_name, data, arg_names=[]):
        header = fn_name + "("

        for item in arg_names:
            header += item + ", "

        header += ") -> Results:"

        print header
        print "------------------------------------------------"
        pprint.pprint(data)
        print "------------------------------------------------\n"

        return None

    def describe_elem_attr_vals_tree(self):
        with open('temp_data/build-tree-tag-k.json') as data_file:    
            data = json.load(data_file)

        data_dict = {}

        for key in data:
            key_obj = data[key]
            count, variations = self.parse_tree_key(key_obj)

            data_dict[key] = { "count" : count, "variations" : variations }


        with open('report_data/tag-count-vari.json', 'w') as f:
            json.dump(data_dict, f, sort_keys=True,
                          indent=4, separators=(',', ': '))

        return data_dict

    def describe_top_attr_vals(self):
        with open('report_data/tag-count-vari.json', 'r') as f:
            data = json.load(f)

        results = []

        for key in sorted(data.iteritems(), key=lambda (k,v): v['count']):
            results.append(key)

        top_ten = results[-10:]
        top_ten = top_ten[::-1]
        with open('report_data/report-count-vari.json', 'w') as f:
            json.dump(top_ten, f, sort_keys=True,
                          indent=4, separators=(',', ': '))
  
    # Store flat dictionary of attr values
    def build_elem_attr_vals_flat(self, elem_name, attr_name):
        print "Working..."
        data = self.count_elem_attr_vals(self.osm_file,
                                         elem_name,
                                         attr_name)
        f_out = "temp_data/"
        f_out += "build-flat-" + elem_name + "-" + attr_name + ".json"

        with open(f_out, 'w') as f:
            json.dump(data, f, sort_keys=True,
                               indent=4, separators=(',', ': '))
        print "Finished!"

        return data

    # Store tree dictionary of attr values
    def build_elem_attr_vals_tree(self, elem_name, attr_name):
        print "Working..."
        data = self.count_elem_attr_vals_tree(self.osm_file,
                                              elem_name,
                                              attr_name)
        f_out = "temp_data/"
        f_out += "build-tree-" + elem_name + "-" + attr_name + ".json"
        
        with open(f_out, 'w') as f:
            json.dump(data, f, sort_keys=True,
                               indent=4, separators=(',', ': '))
        print "Finished!"

        return data

    def count_elem_names(self, filename):
        """ Return dictionary; keys = element names, values = count of element """
        elements = {}

        for _, elem in ET.iterparse(filename):
            if elem.tag in elements:
                elements[elem.tag] += 1
            else:
                elements[elem.tag] = 1

        return elements

    def count_elem_attr(self, filename, elem_name):
        """  """
        attributes = {}

        for _, elem in ET.iterparse(filename):
            if elem.tag == elem_name:

                for item in elem.attrib:
                    if item in attributes:
                        attributes[item] += 1
                    else:
                        attributes[item] = 1

        return attributes

    def count_elem_attr_vals(self, filename, elem_name, attr_name):
        """ Return dictionary; keys = tag key names, values = count of key """

        keys = {}

        for _, elem in ET.iterparse(filename):
            if elem.tag == elem_name:
                attr = elem.get(attr_name)
                if attr in keys:
                    keys[attr] += 1
                else:
                    keys[attr] = 1

        return keys

    def count_elem_attr_vals_tree(self, filename, tag_name, attr_name):

        keys = {}

        for _, elem in ET.iterparse(filename):
            if elem.tag == tag_name:
                attr = elem.get(attr_name)
                keys = self.refactor_parse_key(keys, attr)

        return keys

    def refactor_parse_key(self, keys, tag):
        """" Return keys object with parsed key """
 
        # Recursive base case
        if len(self.split_keys(tag)) == 1:
            if tag in keys:
                if "root" in keys[tag]:
                    keys[tag]["root"] += 1
            else:
                keys[tag] = { "root" : 1 }
            
            return keys

        cur_key = self.split_keys(tag)[0]
        next_key = self.split_keys(tag)[1]

        # Get key value
        cur_obj = keys.get(cur_key)

        if cur_obj:
            next_obj = cur_obj
        else:
            next_obj = {}

        # Recursive call
        updated_keys = self.refactor_parse_key(next_obj, next_key)

        if updated_keys:
            keys[cur_key] = updated_keys
            return keys


    def parse_tree_key(self, obj, count = 0, variations = 0):
        
        for key in obj:
            # Base Case
            if key == "root":
                count +=  obj[key]
                variations += 1
                continue

            new_obj = obj[key]
            count, variations = self.parse_tree_key(new_obj, count, variations)

        return count, variations

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



class OsmCleaner:

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

obj = {
    'address': {
        'root': 1,
        'apartment': {'root': 5},
        'street': {'root': 2}
        },
    'street': {'apartment': {'room': {'root': 1}}}}

obj = {
    "root": 5,
    "street": {
        "root": 7,
        "apt": {
            "root": 3,
            "room": { 
                "root": 8
            }
        }
    }
}




#1.75 million rows of data!
osm_file = "somerville-xml.osm"


if __name__ == '__main__':

    OD = OsmDescribe(osm_file)

    #OD.describe_elem_attr_vals_tree()

    #pprint.pprint(OD.parse_tree_key(obj))

    #OD.describe_elements()

    OD.describe_element_attributes("nd")

    # # Print flat dictionary of attr values
    # OD.describe_element_attribute_values("tag", "k")

    # # Store flat dictionary of attr values
    #OD.build_elem_attr_vals_flat("tag", "k")

    # Store tree dictionary of attr values
    #OD.build_elem_attr_vals_tree("tag", "k")

    #OD.describe_top_attr_vals()
  
    



