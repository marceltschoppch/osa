# xmlparser.py - functions for xml parsing, part of osa.
# Copyright 2013 Sergey Bozhenkov, boz at ipp.mpg.de
# Licensed under GPLv3 or later, see the COPYING file.

"""
    Help functions for dealing with xml.
"""
import xml.etree.cElementTree as etree
import urllib2

default_attr = ["type", "base", "element", "message", "binding", "ref"]

def parse_qualified(f, attr = None):
    """
        Parse xml from file-like object and make changes to qualified values.

        The standard ElementTree parser does not do consider namespaces
        in attribute values. This is however used in wsdl a lot.
        This function uses iterative parser to find the meaning of the
        ns-prefixes and substitutes them with proper values as {...}value.

        Parameters
        ----------
        f : file-like object
            Input source of xml.
        attr : list
            List of attributes whose value must be considered for
            namespace expansion. If none the default_attr is used.

        Returns
        -------
        root : xml node
            Root of the supplied document.
    """
    if attr is None:
        attr = default_attr

    #iterative parsing is done after an example on
    #http://effbot.org/zone/element-namespaces.htm
    ns_map = [] #stack of defined prefixes and values
    events = ("start", "start-ns", "end-ns")
    # start - begin of a new element
    # start-ns - opening of a new namespace
    # end-ns - closing of a namespace
    root = None

    for event, element in etree.iterparse(f, events):
        if event == "start-ns":
            #in this case element is a pair (prefix, value)
            ns_map.append(element)
        elif event == "end-ns":
            ns_map.pop()
        elif event == "start":
            if root is None:
                root = element
            #check that this element has an attribute of interest
            for a in element.attrib.keys():
                if a in attr:
                    #check the attribute value is qualified
                    vlist =  element.attrib[a].split(":")
                    if len(vlist) == 2:
                        #search for the namespace prefix
                        for ns in ns_map:
                            if ns[0] == vlist[0]:
                                #got it
                                element.attrib[a] = "{%s}%s" %(ns[1], vlist[1])
    return root

def parse_qualified_from_url(url, attr = None):
    """
        The same as `parse_qualified`, but xml is given by its url.

        URL is either  http://, or a file if that prefix is not present.
    """
    #open page - get a file like object and
    # parse it into xml
    if url[:7] == "http://":
        page_handler = urllib2.urlopen(url)
    else:
        page_handler = open(url, "r")
    root = parse_qualified(page_handler, attr=attr)
    page_handler.close()
    del page_handler
    return root
