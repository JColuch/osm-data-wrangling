#!/usr/bin/env python
# -*- coding: utf-8 -*-

"OSM Data Wrangling"

__author__ = "Joel Colucci (JoelColucci@Gmail.com)"
__copyright__ = "Copyright (C) 2015 Joel Colucci"
__license__ = "GPL 3.0"
__version__ = ""

import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint
import json
import time

class Utilities:
    """
    """

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

    def count_elem_attr_vals(self, filename, elem_name, attr_name, recursive=False):
        """ Return dictionary; keys = tag key names, values = count of key """

        keys = {}

        for _, elem in ET.iterparse(filename):
            if elem.tag == elem_name:
                attr = elem.get(attr_name)

                if recursive:
                    keys = self.recursive_add_key(keys, attr)
                    continue

                keys = self.add_key(keys, attr)

        return keys

    def add_key(self, keys, attr):
        """  """

        if attr in keys:
            keys[attr] += 1
        else:
            keys[attr] = 1

        return keys

    def recursive_add_key(self, keys, tag):
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
        updated_keys = self.recursive_add_key(next_obj, next_key)

        if updated_keys:
            keys[cur_key] = updated_keys
            return keys

    def recursive_key_count(self, obj, count = 0, variations = 0):
        """  """
        
        for key in obj:
            # Base Case
            if key == "root":
                count +=  obj[key]
                variations += 1
                continue

            new_obj = obj[key]
            count, variations = self.recursive_key_count(new_obj, count, variations)

        return count, variations

    def split_keys(self, key):
        """ Returns list; splits string on colon """

        return key.split(":", 1)

    def fancy_print(self, fn_name, data, arg_names=[]):
        """  """

        header = fn_name + "("

        for item in arg_names:
            header += item + ", "

        header += ") -> Results:"

        print header
        print "------------------------------------------------"
        pprint.pprint(data)
        print "------------------------------------------------\n"

        return None

    def get_data_from_json_file(self, filename):
        """  """

        with open(filename) as data_file:    
            data = json.load(data_file)
        
        return data

    def write_data_to_json_file(self, filename, data):
        """  """

        with open(filename, 'w') as f:
            json.dump(data, f, sort_keys=True,
                          indent=4, separators=(',', ': '))

        return None


class Report(Utilities):
    """
    """

    def __init__(self, filename):
        self.osm_file = filename

    def execute(self):
        """  """

        # Report tag names and frequency
        self.report_elements()

        # Report tag attributes
        self.report_element_attributes("tag")

        # Flat JSON
        self.report_element_attribute_values("tag", "k")

        # Tree JSON
        self.report_element_attribute_values("tag", "k", True)

        # Report tag k summary
        self.report_tag_k_summary()

        # Report top ten k vals by frequency
        self.report_top_k_attr_vals()

        return None

    def report_elements(self):
        """  """

        data = self.count_elem_names(self.osm_file)

        fname_out = "reports/element-types.json"

        self.write_data_to_json_file(fname_out, data)

        return None

    def report_element_attributes(self, elem_name):
        """  """

        data = self.count_elem_attr(self.osm_file, elem_name)

        fname_out = "reports/" + elem_name + "-attributes.json"
        
        self.write_data_to_json_file(fname_out, data)

        return None

    def report_element_attribute_values(self, elem_name, attr_name, recursive=False):
        """ Return flat JSON """

        data = self.count_elem_attr_vals(self.osm_file, elem_name, attr_name, recursive)

        if recursive:
            fname_out = "reports/eav-recursive-" + elem_name + "-" + attr_name + ".json"
        else:
            fname_out = "reports/eav-" + elem_name + "-" + attr_name + ".json"
        
        self.write_data_to_json_file(fname_out, data)

        return None

    def report_tag_k_summary(self):
        """  """

        data = self.count_elem_attr_vals(self.osm_file, "tag", "k", True)

        data_dict = {}

        for key in data:
            key_obj = data[key]
            count, variations = self.recursive_key_count(key_obj)

            data_dict[key] = { "count" : count, "variations" : variations }

        fname_out = "reports/eav-summary-tag-k.json"

        self.write_data_to_json_file(fname_out, data_dict)

        return data_dict

    def report_top_k_attr_vals(self):
        """  """

        #TODO: Handle case where tag-k-summary not yet in existence
        fname_in = "reports/eav-summary-tag-k.json"

        data = self.get_data_from_json_file(fname_in)

        results = []

        for key in sorted(data.iteritems(), key=lambda (k,v): v['count']):
            results.append(key)

        top_ten = results[-10:]
        top_ten = top_ten[::-1]

        fname_out = 'reports/eav-top-tag-k.json'

        self.write_data_to_json_file(fname_out, top_ten)

        return None
  

class Audit(Utilities):

    def __init__(self, filename):
        self.osm_file = filename
        self.regex_lower = re.compile(r'^([a-z]|_)*$')
        self.regex_lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
        self.regex_problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

    def execute(self):
        self.audit_tag_attr("tag", "k")
        
        self.audit_tag_attr("tag", "v")
        
        return None

    def audit_tag_attr(self, target_elm, attr_name):
        keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}

        for _, element in ET.iterparse(self.osm_file):
            keys = self.audit_elem_attr_pattern(keys, element, target_elm, attr_name)

        fname_out = "audits/audit-" + target_elm + "-" + attr_name + ".json"
        self.write_data_to_json_file(fname_out, keys)

        return keys

    def audit_elem_attr_pattern(self, keys, element, target_elm, attr):
        """ Checks key against regex for validity"""

        if element.tag == target_elm:
            val = element.get(attr)

            if re.search(self.regex_problemchars, val):
                keys["problemchars"] += 1

            elif re.search(self.regex_lower, val):
                keys["lower"] += 1

            elif re.search(self.regex_lower_colon, val):
                keys["lower_colon"] += 1

            else:
                keys["other"] += 1

        return keys


class AuditStreet(Audit):
    """
    """

    def __init__(self, filename):
        self.osm_file = filename
        self.expected = ["Street", "Avenue", "Boulevard", "Drive",
                         "Court", "Place", "Square", "Lane",
                         "Road", "Trail", "Parkway", "Commons"]

        self.street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
    
    def audit_street_type(self, street_types, street_name):
        m = self.street_type_re.search(street_name)
        if m:
            street_type = m.group()
            if street_type not in self.expected:
                street_types[street_type].add(street_name)

    def is_street_name(self, elem):
        return (elem.attrib['k'] == "addr:street")

    def audit(self):
        osm_file = open(self.osm_file, "r")
        street_types = defaultdict(set)
        for event, elem in ET.iterparse(self.osm_file, events=("start",)):

            if elem.tag == "node" or elem.tag == "way":
                for tag in elem.iter("tag"):
                    if self.is_street_name(tag):
                        self.audit_street_type(street_types, tag.attrib['v'])

        c_data = self._convert(street_types)
        self.write_data_to_json_file("audits/street-types.json", c_data)

    def _convert(self, data_dict):
        for key in data_dict:
            data_dict[key] = list(data_dict[key])

        return data_dict


class Transform:

    def __init__(self):
        lower = re.compile(r'^([a-z]|_)*$')
        lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
        problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

        CREATED = [ "version", "changeset", "timestamp", "user", "uid"]
        POSITION = ["lat", "lon"]

    def to_json(self, data):
        return json.dumps(data, sort_keys=True,
                         indent=4, separators=(',', ': '))

    def shape_element(self, element):
        node = {}

        if element.tag == "node" or element.tag == "way" :
            # YOUR CODE HERE
            # Add tag type to node
            node["type"] = element.tag

            # Add desired element attributes to node
            node = process_elem_attributes(node, element)

            # Add desired sub-element attributes to node
            node = process_elem_sub_attributes(node, element)
            
            # Reverse order of list so grader is happy
            if "pos" in node:
                node["pos"] = node["pos"][::-1]

            return node
        else:
            return None

    def process_elem_attributes(self, node, element):
        attributes = element.attrib
        #TODO: Add all attributes of node or way tag
        for attribute in attributes:
            value = element.attrib[attribute]

            #TODO: Place CREATED attributes in nested dict
            if attribute in CREATED:
                if "created" not in node:
                    node["created"] = {}

                node["created"][attribute] = value
                continue
            
            #TODO: Place position attributes in nested dict
            if attribute in POSITION:
                if "pos" not in node:
                    node["pos"] = []

                node["pos"].append(float(value))
                continue

            #TODO: Place remaining attributes in dict
            node[attribute] = value

        return node

    def process_elem_sub_attributes(self, node, element):
        sub_elements = element.getiterator()

        for sub_elm in sub_elements:
            if sub_elm.tag == "tag":
                node = process_tag_elem(node, sub_elm)

            if sub_elm.tag == "nd":
                node = process_nd_tag(node, sub_elm)
        
        return node

    def process_tag_elem(self, node, sub_elem):
        k_val = sub_elem.attrib["k"]
        v_val = sub_elem.attrib["v"]

        #TODO: Check for problematic k values
        if contains_bad_char(k_val):
            # Ignore
            return node

        #TODO: Check if compound street
        if is_compound_street_address(k_val):
            # Ignore (example: <tag k="addr:street:prefix" v="North"/>)
            return node
        
        #TODO: Check if starts with "addr:"
        if k_val.startswith("addr:"):
            if "address" not in node:
                node["address"] = {}

            values = k_val.split(":")
            key = values[1]
            node["address"][key] = v_val
        else:
            node[k_val] = v_val

        return node

    def is_compound_street_address(self, string):
        values = string.split(":")
        if len(values) > 2 and values[1] == "street":
            return True

        return False

    def contains_bad_char(self, string):
        return re.search(problemchars, string)

    def process_nd_tag(self, node, sub_elm):
        ref = sub_elm.attrib["ref"]

        if "node_refs" in node:
            node["node_refs"].append(ref)
        else:
            node["node_refs"] = [ref]

        return node

    def process_map(self, file_in, pretty = False):
        # You do not need to change this file
        file_out = "{0}.json".format(file_in)
        data = []
        with codecs.open(file_out, "w") as fo:
            for _, element in ET.iterparse(file_in):
                el = shape_element(element)
                if el:
                    data.append(el)
                    if pretty:
                        fo.write(json.dumps(el, indent=2)+"\n")
                    else:
                        fo.write(json.dumps(el) + "\n")
        return data


class Load:

    def __init__(self):
        pass


class Clean:

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


def main():
    start = time.clock()

    osm_file = "somerville-xml.osm"

    #reporter = Report(osm_file)
    #reporter.execute()

    # auditor = Audit(osm_file)
    # auditor.execute()

    aud = AuditStreet(osm_file)
    aud.audit()

    end = time.clock()
    print "Execution time: " + str(end-start)


if __name__ == '__main__':
    main()


    





