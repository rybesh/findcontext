from piston.emitters import XMLEmitter, JSONEmitter
from main.models import Resource
from lxml import etree
import json

class CustomXMLEmitter(XMLEmitter):
    def render(self, request):
        if isinstance(self.data, Resource):
            return etree.tostring(self.data.open_search_description, 
                                  encoding='UTF-8', pretty_print=True)
        return super(CustomXMLEmitter, self).render(request)

class CustomJSONEmitter(JSONEmitter):
    @classmethod
    def element_to_dict(cls, e, parent):
        # see http://code.google.com/apis/gdata/docs/json.html
        if isinstance(e.tag, basestring):
            d = {}
            # convert namespaced tag name to key
            key = e.tag
            for prefix, ns in e.nsmap.iteritems():
                # add xmlns values to root object
                if len(parent) == 0:
                    xmlns = 'xmlns'
                    if prefix: xmlns += '$%s' % prefix
                    d[xmlns] = ns
                if prefix: prefix = '%s$' % prefix
                key = key.replace('{%s}' % ns, prefix or '')
            # recursively build our dict
            d.update(e.attrib)
            if e.text and e.text.strip(): 
                d['$t'] = e.text
            for child in e:
                cls.element_to_dict(child, d)
            # add dict to parent
            if key in parent:
                if isinstance(parent[key], list):
                    parent[key].append(d)
                else:
                    parent[key] = [ parent[key], d ]
            else:
                parent[key] = d
        return parent
    def render(self, request):
        if isinstance(self.data, Resource):
            return json.dumps(
                self.element_to_dict(self.data.open_search_description, {}))
        return super(CustomJSONEmitter, self).render(request)


