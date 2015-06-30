#!/usr/bin/env python

"""Module contains functions to transform OSM XML data
into JSON documents ready to be uploaded to mongodb.
"""

import codecs
import json
import re
import streetauditor
import xml.etree.ElementTree as ET


LOWER = re.compile(r'^([a-z]|_)*$')
LOWER_COLON = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
PROBLEM_CHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

DESIRED = ["id", "type", "visible", "amenity", "cuisine", "name", "phone"]
CREATED = ["version", "changeset", "timestamp", "user", "uid"]
POSITION = ["lat", "lon"]


def process_map(file_in, pretty=False):
    """Transform XML data into JSON document schema for mongodb upload"""
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as file_out:
        for _, element in ET.iterparse(file_in):
            elem = shape_element(element)
            if elem:
                data.append(elem)
                if pretty:
                    file_out.write(json.dumps(elem, indent=2)+"\n")
                else:
                    file_out.write(json.dumps(elem) + "\n")
    return data


def shape_element(element):
    """Transform XML element into dictionary representation"""
    node = {}

    if element.tag == "node" or element.tag == "way":
        node["type"] = element.tag
        # Add desired element attributes to node.
        node = transform_element_attributes(node, element)

        # Add desired sub-element attributes to node.
        node = transform_sub_elem_attributes(node, element)

        return node
    else:
        return None


def transform_element_attributes(node, element):
    """Transform and add element attributes to node"""
    #Get all attributes of XML element.
    attributes = element.attrib

    for attribute in attributes:
        value = element.attrib[attribute]
        # Capture special attrs in CREATED collection and add to nested dict.
        if attribute in CREATED:
            if "created" not in node:
                node["created"] = {}
            node["created"][attribute] = value
        # Capture lat, lon  attributes and add to nested dict "pos".
        elif attribute in POSITION:
            if "pos" not in node:
                node["pos"] = []
            # Ensure proper order of lat, lon in list.
            if attribute == "lat":
                node["pos"].insert(0, float(value))
            else:
                node["pos"].append(float(value))
        elif attribute in DESIRED:
            # Place attribute in dict.
            node[attribute] = value

    return node


def transform_sub_elem_attributes(node, element):
    """Transform and add sub elements to node"""
    sub_elements = element.getiterator()

    for sub_elm in sub_elements:
        if sub_elm.tag == "tag":
            node = transform_tag_elem(node, sub_elm)

        if sub_elm.tag == "nd":
            node = transform_nd_tag(node, sub_elm)

    return node


def transform_tag_elem(node, sub_elem):
    """Extracts and adds tag element specific attributes"""
    k_val = sub_elem.attrib["k"]
    v_val = sub_elem.attrib["v"]

    # Catch and ignore problematic k values.
    if contains_bad_char(k_val) or is_compound_street_address(k_val):
        return node

    # Catch address related k values.
    if k_val.startswith("addr:"):
        if "address" not in node:
            node["address"] = {}

        values = k_val.split(":")
        key = values[1]

        # If applicable, normalize street name.
        if key == 'street':
            v_val = streetauditor.normalize_name(v_val)

        node["address"][key] = v_val
    elif k_val in DESIRED:
        node[k_val] = v_val

    return node


def transform_nd_tag(node, sub_elm):
    """Extracts and adds nd tag specific attributes"""
    ref = sub_elm.attrib["ref"]

    if "node_refs" in node:
        node["node_refs"].append(ref)
    else:
        node["node_refs"] = [ref]

    return node


def is_compound_street_address(string):
    """Returns true if string is a compound address"""
    values = string.split(":")
    if len(values) > 2 and values[1] == "street":
        return True

    return False


def contains_bad_char(string):
    """Returns true if string contains problematic characters"""
    return re.search(PROBLEM_CHARS, string)


if __name__ == "__main__":
    OSM_FILE = 'data/somerville-xml.osm'
    process_map(OSM_FILE, True)
