#!/usr/bin/env python

"""Module contains functions to audit and normalize street names.
"""


from collections import defaultdict
import re
import xml.etree.cElementTree as ET


EXPECTED = ["Street", "Avenue", "Boulevard", "Drive",
            "Court", "Place", "Square", "Lane",
            "Road", "Trail", "Parkway", "Commons",
            "Elm", "West", "Hampshire", "Cambridge",
            "Broadway", "Circle", "East", "Highway",
            "Center", "Park", "Fellsway", "Holland",
            "Terrace", "Row", "Way"]

STREET_RE = re.compile(r'\b\S+\.?$', re.IGNORECASE)

MAPPING = {
    "St": "Street",
    "ST": "Street",
    "St.": "Street",
    "st": "Street",
    "St,": "Street",
    "ave": "Avenue",
    "Ave.": "Avenue",
    "Ave": "Avenue",
    "Pl": "Place",
    "Hwy": "Highway",
    "Sq": "Square",
    "Pkwy": "Parkway",
    "Ct": "Court",
    "Rd": "Road",
    "LEVEL": "Level"
}


def audit(filename):
    """Identify and transform non-expected street names."""
    street_types = defaultdict(set)

    for _, elem in ET.iterparse(filename, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])

    return street_types


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


def normalize_name(street_type):
    """Transform streetname to desired format."""
    normalized_street = street_type

    match = re.search(STREET_RE, street_type)
    if match:
        match_str = match.group(0)
        #If street name is not valid, normalize it.
        if match_str not in EXPECTED:
            #Get mapping, if no mapping available default to the same.
            new_name = MAPPING.get(match_str, match_str)
            normalized_street = re.sub(match_str, new_name, street_type)

    return normalized_street


if __name__ == '__main__':
    OSM_FILE = 'data/somerville-xml.osm'
    print dict(normalize_street_names(OSM_FILE))
