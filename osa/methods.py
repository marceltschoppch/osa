"""
    Classes required for remote method calls: messages and method wrappers.
"""
from soap import *
from exceptions import ValueError, RuntimeError
from urllib2 import urlopen, Request, HTTPError
import xml.etree.cElementTree as etree

class Message(object):
    """
        Message for input and output of service operations.

        Messages perform conversion of Python to xml and backwards
        of the calls and returns.

        A message instance knows about used style/literal convention and can
        use it to perform transformations. At the moment only
        document/literal wrapped is implemented. You can improve this class
        to have the others.

        .. warning::
            Only document/literal wrapped convention is implemented at the moment.

        Parameters
        ----------
        tag : str
            Name of the message.
        namespafe : str
            Namespace of the message.
        parts : list
            List of message parts in the form
            (part name, part type class).
            This description is usually found in message part of a WSDL document.
        style : str
            Operation style document/rpc.
        literal : bool
            True = literal, False = encoded.
    """
    def __init__(self, tag, namespace, parts, style, literal):
        self.tag = tag
        self.namespace = namespace
        self.parts = parts
        self.style = style
        self.literal = literal


    def __str__(self, switch = "wrap"):
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
        if self.style != "document" or not(self.literal):
            raise RuntimeError(
                "Only document/literal are supported. Improve Message class!")
        #assumed wrapped convention
        p = self.parts[0][1] #message type
        res = ''
        if switch == "positional":
            for child in p._children:
                opt = ''
                array = ''
                if child['max']>1:
                     # 'unbounded'>1
                     array = '[]'
                if child['min']==0:
                    opt = '| None'
                type = get_local_type(child['type'].__name__)
                res = res + ', %s%s %s %s'\
                        %(type, array, child["name"], opt)
        elif switch == "keyword":
            for child in p._children:
                opt = ''
                array = ''
                if child['max']>1:
                     # 'unbounded'>1
                     array = '[]'
                if child['min']==0:
                    opt = '| None'
                type = get_local_type(child['type'].__name__)
                res = res + ', %s=%s%s %s'\
                        %(child['name'], type, array, opt)
        elif switch == 'out' and len(p._children) == 1:
            child = p._children[0]
            opt = ''
            array = ''
            if child['max']>1:
                 # 'unbounded'>1
                 array = '[]'
            if child['min']==0:
                opt = '| None'
            type = get_local_type(child['type'].__name__)
            res = '%s%s %s %s'  %(type, array, 'result', opt)
        else:
            res = '%s %s' %(p.__name__, 'msg')

        if len(res)>2 and res[0] == ',':
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
        if self.style != "document" or not(self.literal):
            raise RuntimeError(
                "Only document/literal are supported. Improve Message class!")

        #assumed wrapped convention
        p = self.parts[0][1]() #encoding instance

        #wrapped message is supplied
        if len(arg) == 1 and isinstance(arg[0], self.parts[0][1]):
            for child in p._children:
                setattr(p, child['name'], getattr(arg[0], child['name'], None))
        else:
            #reconstruct wrapper from expanded input
            counter = 0
            for child in p._children:
                name = child["name"]
                #first try keyword
                val = kw.get(name, None)
                if val is None: #not keyword
                    if counter < len(arg):
                        #assume this is positional argument
                        val = arg[counter]
                        counter = counter + 1
                if val is None: #check if nillable
                    if child["min"] == 0:
                        continue
                    else:
                        raise ValueError(\
                                "Non-nillable parameter %s is not present"\
                                                                    %name)
                setattr(p, name, val)

        #the real conversion is done by ComplexType
        p.to_xml(kw["_body"], "{%s}%s" %(self.namespace, self.tag))

    def from_xml(self, body, header = None):
        """
            Convert from xml message to Python.
        """
        if self.style != "document" or not(self.literal):
            raise RuntimeError(
                "Only document/literal are supported. Improve Message class.")

        #assumed wrapped convention
        p = self.parts[0][1]() #decoding instance

        res = p.from_xml(body)

        #for wrapped doc style (the only one implemented) we know, that
        #wrapper has only one child, get it
        if len(p._children) == 1:
            return getattr(res, p._children[0]["name"], None)
        else:
            return res

class Method(object):
    """
        Definition of a single SOAP method, including location, action, name
        and input and output classes.

        Parameters
        ----------
        location : str
            Location as found in service part of WSDL.
        name : str
            Name of operation
        action : str
            Action (?) as found in binding part of WSDL.
        input : Message instance
            Input message description.
        output : Message instance
            Output message description.
        doc : str, optional - default to None
            Documentation of the method as found in portType section of WSDL.
    """
    def __init__(self, location, name, action, input, output, doc=None):
        self.location = location
        self.name = name
        self.action = action
        self.input = input
        self.output = output
        #add call signatures to doc
        sign = '%s\n%s\n%s' %(self.__str__(),
                                            self.__str__(switch="positional"),
                                            self.__str__(switch="keyword"))
        self.__doc__ = '%s\n%s' %(sign, doc)

    def __str__(self, switch = 'wrap'):
        """
            String representation of the call in three forms:
                - wrapped message
                - positional sub-arguments
                - keyword sub-arguments.

            Parameters
            ----------
            switch : str, optional
                Specifies which form to return: wrap, positional, keyword.
        """
        input_msg = self.input.__str__(switch = switch)
        output_msg = self.output.__str__(switch = 'out')

        return '%s = %s(%s)' %(output_msg, self.name, input_msg)


    def __call__(self, *arg, **kw):
        """
            Process rpc-call.
        """
        #create soap-wrap around our message
        env = etree.Element('{%s}Envelope' %NS_SOAP_ENV)
        header = etree.SubElement(env, '{%s}Header' %NS_SOAP_ENV)
        body = etree.SubElement(env, '{%s}Body' %NS_SOAP_ENV)

        #compose call message - convert all parameters and encode the call
        kw["_body"] = body
        self.input.to_xml(*arg, **kw)

        text_msg = etree.tostring(env) #message to send
        del env

        #http stuff
        request = Request(self.location, text_msg,
                                {'Content-Type': 'text/xml',
                                'SOAPAction': self.action})
        del text_msg

        #real rpc
        try:
            response = urlopen(request).read()
            del request
            #string to xml
            xml = etree.fromstring(response)
            del response
            #find soap body
            body = xml.find(SOAP_BODY)
            if body is None:
                raise RuntimeError("No SOAP body found in response")
            body = body[0] # hacky? get the first real element
        except HTTPError, e:
            if e.code in (202,204):
                return None
            elif e.code == 500:
                #read http error body and make xml from it
                xml = etree.fromstring(e.fp.read())
                body = xml.find(SOAP_BODY)
                if body is None:
                    raise
                #process service fault
                fault = body.find(SOAP_FAULT)
                if fault is not None:
                    code = fault.find('faultcode')
                    if code is not None:
                        code = code.text or ''
                    string = fault.find('faultstring')
                    if string is not None:
                        string = string.text or ''
                    detail = fault.find('detail')
                    if detail is not None:
                        detail = detail.text or ''
                    raise RuntimeError("SOAP Fault %s:%s <%s> %s%s"\
                            %(self.location, self.name, code, string, detail))
                else:
                    raise
            else:
                raise

        return self.output.from_xml(body)

