# scio/autowsdl.py -- soap classes for input and output
#
# Copyright (c) 2011, Leapfrog Direct Response, LLC
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Leapfrog Direct Response, LLC, including
#       its subsidiaries and affiliates nor the names of its
#       contributors, may be used to endorse or promote products derived
#       from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL LEAPFROG DIRECT
# RESPONSE, LLC, INCLUDING ITS SUBSIDIARIES AND AFFILIATES, BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os

from docutils import nodes
from docutils.parsers.rst import directives
from docutils.statemachine import ViewList
from sphinx.util.compat import Directive

import scio, scio.client

class AutoWsdl(Directive):
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {'namespace': directives.unchanged}
    has_content = False
    ns = 'unknown'
    client = None

    def run(self):
        wsdl_file = self.arguments[0]
        self.ns = self.options.get('namespace', self.ns_from_file(wsdl_file))
        self.client = scio.Client(open(wsdl_file, 'r')) # FIXME accept urls too?
        rst = self.doc()
        state = self.state
        node = nodes.section()
        surrounding_title_styles = state.memo.title_styles
        surrounding_section_level = state.memo.section_level
        state.memo.title_styles = []
        state.memo.section_level = 0
        state.nested_parse(rst, 0, node, match_titles=1)
        state.memo.title_styles = surrounding_title_styles
        state.memo.section_level = surrounding_section_level
        return node.children

    def ns_from_file(self, filename):
        bn = os.path.basename(filename)
        bn, _ext = os.path.splitext(bn)
        return bn

    def doc(self):
        client = self.client
        buf = ViewList()
        name = client.wsdl.wsdl.get(
            'name', client.wsdl.wsdl.get('targetNamespace', '(unnamed)'))
        title = 'Web Service: %s' % name
        buf.append(title, '<autowsdl>')
        buf.append('=' * len(title), '<autowsdl>')
        buf.append('', '<autowsdl>')

        buf.append('Methods', '<autowsdl>')
        buf.append('-------', '<autowsdl>')
        buf.append('', '<autowsdl>')
        buf.append("Methods are accessible under the ``service`` attribute "
                      "of a client instance.", '<autowsdl>')
        buf.append('', '<autowsdl>')
        for entry in dir(client.service):
            # print 'method', entry
            if entry.startswith('_') or entry == 'method_class':
                continue
            item = getattr(client.service, entry)
            try:
                doc = self.doc_method(item.method)
                if doc is not None:
                    buf.extend(doc)
            except AttributeError, e:
                print "failed method", entry, e
                pass
        buf.append('', '<autowsdl>')
        buf.append('Types', '<autowsdl>')
        buf.append('-----', '<autowsdl>')
        buf.append('', '<autowsdl>')
        buf.append("Types are accessible under the ``type`` attribute "
                      "of a client instance.", '<autowsdl>')
        buf.append('', '<autowsdl>')
        for entry in dir(client.type):
            if entry.startswith('_'):
                continue
            item = getattr(client.type, entry)
            try:
                doc = self.doc_type(item)
                if doc is not None:
                    buf.extend(doc)
            except AttributeError, e:
                print "failed type", entry, e
                pass

        return buf

    def doc_type(self, cls):
        buf = ViewList()
        buf.append('.. class :: %s.%s' % (self.ns, cls.__name__), '<autowsdl>')
        buf.append('', '<autowsdl>')
        if issubclass(cls, scio.client.EnumType):
            buf.append('   Values: ', '<autowsdl>')
            buf.append('', '<autowsdl>')
            for val in cls._values:
                buf.append('   * %s' % val, '<autowsdl>')
                buf.append('', '<autowsdl>')
        else:
            if getattr(cls, '_content_type', None):
                buf.append('   .. attribute :: _content', '<autowsdl>')
                buf.append('', '<autowsdl>')
                buf.append(
                    '      type: :class:`%s.%s`' % (self.ns,
                                                    cls._content_type.__name__),
                    '<autowsdl>')
                buf.append('', '<autowsdl>')
            for a in getattr(cls, '_attributes', []):
                buf.append('   .. attribute :: %s' % a.name, '<autowsdl>')
                buf.append('', '<autowsdl>')
            for c in getattr(cls, '_children', []):
                buf.append('   .. attribute :: %s' % c.name, '<autowsdl>')
                buf.append('', '<autowsdl>')
                if issubclass(c.type, (scio.client.ComplexType,
                                       scio.client.EnumType)):
                    buf.append('      type: :class:`%s.%s`' % (self.ns,
                                                               c.type.__name__),
                                  '<autowsdl>')
                else:
                    buf.append('      type: %s.%s' % (self.ns, c.type.__name__),
                               '<autowsdl>')

                descr = getattr(cls, c.name, None)
                if (descr and
                    descr.max and
                    (descr.max == 'unbounded' or descr.max > 1)):
                    msg = '      This is a list with'
                    if descr.max == 'unbounded' :
                        msg += " an unlimited number of items."
                    else:
                        msg += "at most %s items." % descr.max
                    buf.append('      ', '<autowsdl>')
                    buf.append(msg, '<autowsdl>')

                subs = getattr(c.type, '_substitutions', {})
                if subs:
                    buf.append('      ', '<autowsdl>')
                    buf.append('      This attribute may contain any of the '
                               'following types: ', '<autowsdl>')
                    for name in sorted(subs.keys()):
                        buf.append('       - :class:`%s.%s`' % (self.ns, name),
                                   '<autowsdl>')
                buf.append('', '<autowsdl>')
        return buf

    def doc_method(self, meth):
        buf = ViewList()
        details = []
        req = []
        opt = []
        # print 'meth', meth, meth.input, meth.input.parts
        if meth.input.parts:
            for part_name, cls in meth.input.parts:
                param_details, param_req, param_opt = self.doc_param(part_name, cls)
                details.extend(param_details)
                req.extend(param_req)
                opt.extend(param_opt)
        else:
            # FIXME is this correct?
            c = meth.input
            name = c.name or c.__name__
            req.append(name)
            details.append('   :param %s: :class:`%s.%s`' %
                           (name, self.ns, c.__name__))
        if meth.input.headers:
            for part_name, cls in meth.input.headers:
                param_details, param_req, param_opt = self.doc_param(part_name, cls)
                details.extend(param_details)
                req.extend(param_req)
                opt.extend(param_opt)

        rtypes = []
        # print meth.name, meth.output.parts
        if meth.output.parts:
            rtypes = [':class:`%s.%s`' % (self.ns, cls.__name__)
                      for _, cls in meth.output.parts]
        #print meth.name, meth.output.headers
        if meth.output.headers:
            rtypes.append(
                '{%s}' % ', '. join('%s: :class:`%s.%s`' % (name,
                                                            self.ns,
                                                            cls.__name__)
                                    for name, cls in meth.output.headers))
        if len(rtypes) == 1:
            details.append('   :rtype: %s' % rtypes[0])
        elif len(rtypes) > 1:
            details.append('   :rtype: (%s)' %
                           ', '.join(rtypes))
        signature = ', '.join(req)
        if opt:
            signature += '[' + ', '.join(opt) + ']'
        buf.append('.. method :: %s.%s(%s)' % (self.ns, meth.name, signature),
                      '<autowsdl>')
        buf.append('', '<autowsdl>')
        for d in details:
            buf.append(d, '<autowsdl')
        return buf

    def doc_param(self, part_name, cls):
        details = []
        req = []
        opt = []
        kids = getattr(cls, '_children', ())
        kids = kids + getattr(cls, '_attributes', ())
        if kids:
            for c in kids:
                if c.min:
                    min = int(c.min)
                else:
                    min = 0
                if min > 0 or c.required:
                    req.append(c.name)
                    desc = ''
                else:
                    opt.append(c.name)
                    desc = ' (optional)'
                details.append('   :param %s: :class:`%s.%s`%s' %
                               (c.name, self.ns, c.type.__name__, desc))
        else:
            name = part_name or cls._tag
            # FIXME is this correct?
            if name:
                # print "Arg?", name, cls
                req.append(name)
                details.append('   :param %s: :class:`%s.%s`' %
                               (name, self.ns, cls.__name__))
        return details, req, opt


def setup(app):
    app.add_directive('autowsdl', AutoWsdl)


