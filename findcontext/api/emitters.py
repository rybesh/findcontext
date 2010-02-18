import json
from datetime import datetime
from django.contrib.sites.models import Site
from django.db.models.query import QuerySet
from django.utils import feedgenerator
from lxml import etree
from lxml.builder import ElementMaker
from findcontext.main.models import Resource, Package
from piston.emitters import XMLEmitter, JSONEmitter

ATOM_NS = 'http://www.w3.org/2005/Atom'
a = ElementMaker(namespace=ATOM_NS, nsmap={ None: ATOM_NS })


class OSDEmitter(XMLEmitter):

    def render(self, request):
        if isinstance(self.data, Resource):
            return etree.tostring(self.data.open_search_description, 
                                  encoding='utf-8', pretty_print=True,
                                  xml_declaration=True)
        return super(OSDEmitter, self).render(request)


class AtomEmitter(XMLEmitter):

    @classmethod
    def package_to_atom(cls, package):
        return cls.resources_to_atom(
            package.resources.all(), package.name, package.description,
            package.last_updated, package.uri)
    
    @classmethod
    def resources_to_atom(cls, resources, 
                          name='All resources', 
                          description='All available resources.',
                          updated=datetime.now(),
                          package_uri=None):
        if not package_uri:
            package_uri = 'http://%s/api/resource/' % Site.objects.get_current().domain
        feed = a.feed(
            a.title(name),
            a.id(package_uri),
            a.updated(feedgenerator.rfc3339_date(updated)),
            a.subtitle(description),
            a.link(rel='self', href=package_uri))
        for resource in resources:
            feed.append(a.entry(
                    a.title(resource.short_name),
                    a.id(resource.uri),
                    a.updated(feedgenerator.rfc3339_date(resource.last_updated)),
                    a.summary(resource.description),
                    a.author(a.name(resource.developer)),
                    a.content(
                        resource.open_search_description,
                        type='application/opensearchdescription+xml')))
        return feed

    def serialize(self, doc):
        return etree.tostring(doc, encoding='utf-8', pretty_print=True,
                              xml_declaration=True)

    def render(self, request):
        if isinstance(self.data, Package):
            return self.serialize(self.package_to_atom(self.data))
        if isinstance(self.data, QuerySet):
            return self.serialize(self.resources_to_atom(self.data))
        return super(AtomEmitter, self).render(request)    


class CustomJSONEmitter(JSONEmitter):

    @classmethod
    def element_to_dict(cls, e, parent, nsmap={}):
        # see http://code.google.com/apis/gdata/docs/json.html
        if isinstance(e.tag, basestring):
            d = {}
            # deal with namespaces
            key = e.tag
            changed_prefixes = []
            for prefix, ns in e.nsmap.iteritems():
                nss = nsmap.get(prefix, [])
                if len(nss) == 0 or not ns == nss[-1]:
                    nss.append(ns)
                    nsmap[prefix] = nss
                    changed_prefixes.append(prefix)
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
                cls.element_to_dict(child, d, nsmap)
            # pop changed prefixes
            for prefix in changed_prefixes:
                nsmap[prefix].pop()
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
                self.element_to_dict(
                    self.data.open_search_description, {}))
        if isinstance(self.data, Package):
            return json.dumps(
                self.element_to_dict(
                    AtomEmitter.package_to_atom(self.data), {}))
        return super(CustomJSONEmitter, self).render(request)


