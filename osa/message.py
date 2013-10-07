# message.py - Message class, part of osa.
# Copyright 2013 Sergey Bozhenkov, boz at ipp.mpg.de
# Licensed under LGPLv3 or later, see the COPYING file.

"""
   Python class for input/output messages.
"""
# from . import xmlnamespace
from . import xmltypes
# import xml.etree.cElementTree as etree


class Message(object):
    """
        Message for input and output of service operations.

        Messages perform conversion of Python to xml and backwards
        of the calls and returns.

        At the moment only document/literal wrapped is implemented.

        Parameters
        ----------
        name : str
            Namespace qualified name of the message.
        parts : list
            List of message parts in the form
            (part name, part type class).
            This description is usually found in message part of a WSDL document.
            Note, that due to binding section not all message parts are used for encoding.
            The parts that are used are given be use_parts.
        use_parts : list
            List of parts to be really used for encoding/decoding.
            This comes from wsdl binding section. Yes, they are not
            quite from this planet.
            In any case, in the present implementation I assume doc/literal wrapped and
            use only the very first part from this member for encoding.
    """
    def __init__(self, name, parts, use_parts=None):
        self.name = name
        self.parts = parts
        if use_parts is None:
            use_parts = []
        self.use_parts = use_parts

    def __str__(self, switch="wrap"):
        """
            String representation of the message in three forms:
                - wrapped message
                - positional sub-arguments
                - keyword sub-arguments.
                - out - the only child of wrapped message. This applicable
                        to output message extraction.

            Parameters
            ----------
            switch : str, optional
                Specifies which form to return: wrap, positional, keyword, out.
        """
        # assumed wrapped convention
        if len(self.use_parts) < 1:
            return ""
        p = self.use_parts[0][1]  # message type
        res = ''
        if switch == "positional":
            for child in getattr(p, "_children", []):
                opt = ''
                array = ''
                if child['max'].__class__.__name__ != "int" or child['max'] > 1:
                    array = '[]'
                if child['min'] == 0:
                    opt = '| None'
                type = xmltypes.get_local_type(child['type'].__name__)
                res = '%s, %s%s %s %s' % (res, type, array, child["name"], opt)
        elif switch == "keyword":
            for child in getattr(p, "_children", []):
                opt = ''
                array = ''
                if child['max'].__class__.__name__ != "int" or child['max'] > 1:
                    array = '[]'
                if child['min'] == 0:
                    opt = '| None'
                type = xmltypes.get_local_type(child['type'].__name__)
                res = '%s, %s=%s%s %s' % (res, child['name'], type, array, opt)
        elif switch == 'out' and len(getattr(p, "_children", [])) == 1:
            child = p._children[0]
            opt = ''
            array = ''
            if child['max'].__class__.__name__ != "int" or child['max'] > 1:
                array = '[]'
            if child['min'] == 0:
                opt = '| None'
            type = xmltypes.get_local_type(child['type'].__name__)
            res = '%s%s %s %s' % (type, array, 'result', opt)
        else:
            res = '%s %s' % (p.__name__, 'msg')

        if len(res) > 2 and res[0] == ',':
            res = res[2:]

        return res

    def to_xml(self, *arg, **kw):
        """
            Convert from Python into xml message.

            This function accepts parameters as they are supplied
            to the method call and tries to convert it to a message.
            Arguments can be in one of  four forms:
                - 1 argument of proper message type for this operation
                - positional arguments - members of the proper message type
                - keyword arguments - members of the message type.
                - a mixture of positional and keyword arguments.

            Keyword arguments must have at least one member: _body which
            contains etree.Element to append the conversion result to.
        """
        if len(self.use_parts) < 1:
            # etree.SubElement(kw["_body"], self.name)
            return
        # assumed wrapped convention
        cl = self.use_parts[0][1]  # class
        p = cl()  # encoding instance

        # wrapped message is supplied
        if len(arg) == 1 and isinstance(arg[0], cl):
            for child in getattr(p, "_children", []):
                p = arg[0]
        else:
            # reconstruct wrapper from expanded input
            counter = 0
            for child in getattr(p, "_children", []):
                name = child["name"]
                # first try keyword
                val = kw.get(name, None)
                if val is None:  # not keyword
                    if counter < len(arg):
                        # assume this is positional argument
                        val = arg[counter]
                        counter += 1
                if val is None:  # check if nillable
                    if child["min"] == 0:
                        continue
                    else:
                        raise ValueError("Non-nillable parameter %s is not "
                                         "present" % name)
                setattr(p, name, val)

        # set default ns to save space
        # this does not work with xml qualified/unqualified, need a hack
        # etree.register_namespace("", xmlnamespace.get_ns(self.name))
        # the real conversion is done by ComplexType
        # messages always refer to a top level element => qualified
        p.to_xml(kw["_body"], "{%s}%s" % (p._namespace, p.__class__.__name__))

    def from_xml(self, body, header=None):
        """
            Convert from xml message to Python.
        """
        if len(self.use_parts) < 1:
            return None
        # assumed wrapped convention
        p = self.use_parts[0][1]()  # decoding instance

        res = p.from_xml(body)

        # for wrapped doc style (the only one implemented) we know, that
        # wrapper has only one child, get it
        if len(getattr(p, "_children", [])) == 1:
            return getattr(res, p._children[0]["name"], None)
        else:
            return res
