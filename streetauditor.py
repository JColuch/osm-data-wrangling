#!/usr/bin/env python

"""Module contains functions to audit and normalize street names.
"""


from collections import defaultdict
import re
import xml.etree.cElementTree as ET


EXPECTED = ["Street", "Avenue", "Boulevard", "Drive",
            "Court", "Place", "Square", "Lane",
            "Road", "Trail", "Parkway", "Commons"]

STREET_RE = re.compile(r'\b\S+\.?$', re.IGNORECASE)


def normalize_street_names(filename):
    """Identify and transform non-expected street names."""
    street_types = defaultdict(set)

    for _, elem in ET.iterparse(filename, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])

    c_data = _convert(street_types)

    return c_data, street_types


def audit_street_type(street_types, street_name):
    """Validate if street name type is allowed."""
    match = STREET_RE.search(street_name)
    if match:
        street_type = match.group()
        if street_type not in EXPECTED:
            street_types[street_type].add(street_name)


def is_street_name(elem):
    """Determine if element k attribute describes a street."""
    return elem.attrib['k'] == "addr:street"


def _convert(data_dict):
    """Map list values to dictionary."""
    for key in data_dict:
        data_dict[key] = list(data_dict[key])

    return data_dict


if __name__ == '__main__':
    pass
