#!/usr/bin/env python

"""Module contains functions that provide high level overview of
OSM XML data.
"""


import xml.etree.cElementTree as ET


def get_top_level_tag_summary(filename):
    """Return dict containing name and count of top level tags."""
    tags = {}

    for _, elem in ET.iterparse(filename):
        if elem.tag in tags:
            tags[elem.tag] += 1
        else:
            tags[elem.tag] = 1

    return tags


def get_number_of_contributors(filename):
    """Return number of unique map contributors."""
    users = set()

    for _, element in ET.iterparse(filename):
        uid = element.get("uid")
        if uid:
            users.add(uid)

    return len(users)


if __name__ == '__main__':
    OSM_FILE = 'data/somerville-xml.osm'
    print get_top_level_tag_summary(OSM_FILE)
