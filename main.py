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

        elements_data = self.count_elem_names(self.osm_file)
        print "describe_elements() -> Results:" 
        print "------------------------------------------------"
        pprint.pprint(elements_data)
        print "------------------------------------------------\n"

        return None

    def describe_element_attributes(self, elem_name):
        print "Working...\n"

        element_attr_data = self.count_elem_attr(self.osm_file, elem_name)
        print "describe_element_attributes(" + elem_name + ") -> Results:"
        print "------------------------------------------------"
        pprint.pprint(element_attr_data)
        print "------------------------------------------------\n"

        return None

    def describe_element_attribute_values(self, elem_name, attr_name):
        print "Working...\n"

        elements_attr_val_data = self.count_elem_attr_vals(self.osm_file,
                                                           elem_name,
                                                           attr_name)
        msg = "describe_element_attribute_values(" + elem_name + ", "
        msg += attr_name + ") -> Results:"
        print msg
        print "------------------------------------------------"
        pprint.pprint(elements_attr_val_data)
        print "------------------------------------------------\n"

        return None

    # Store flat dictionary of attr values
    def build_elem_attr_vals_flat(self, elem_name, attr_name):
        data = self.count_elem_attr_vals(self.osm_file,
                                         elem_name,
                                         attr_name)
        f_out = "temp_data/"
        f_out += "build-flat-" + elem_name + "-" + attr_name + ".json"

        with open(f_out, 'w') as f:
            json.dump(data, f)

    # Store tree dictionary of attr values
    def build_elem_attr_vals_tree(self, elem_name, attr_name):
        data = self.count_elem_attr_vals_tree(self.osm_file,
                                              elem_name,
                                              attr_name)
        f_out = "temp_data/"
        f_out += "build-tree-" + elem_name + "-" + attr_name + ".json"
        
        with open(f_out, 'w') as f:
            json.dump(data, f)
    



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

    #Possible to use static method decorator here
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

    osm_describe = OsmDescribe(osm_file)

    # osm_describe.describe_elements()

    # osm_describe.describe_element_attributes("nd")

    # # Print flat dictionary of attr values
    # osm_describe.describe_element_attribute_values("tag", "k")

    # # Store flat dictionary of attr values
    #osm_describe.build_elem_attr_vals_flat("tag", "k")

    # # Store tree dictionary of attr values
    #osm_describe.build_elem_attr_vals_tree("tag", "k")




  
    



