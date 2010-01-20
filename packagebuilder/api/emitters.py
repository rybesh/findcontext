from piston.emitters import XMLEmitter, JSONEmitter
from django.utils import feedgenerator
from django.contrib.sites.models import RequestSite
from main.models import Resource, Package
from lxml import etree
from lxml.builder import ElementMaker
import json

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
    def package_to_atom(cls, request, package):
        domain = RequestSite(request).domain
        package_url = 'http://%s%s' % (domain, package.get_absolute_url())
        feed = a.feed(
            a.title(package.name),
            a.id(package_url),
            a.updated(feedgenerator.rfc3339_date(package.last_updated)),
            a.subtitle(package.description),
            a.link(rel='self', href=package_url))
        for resource in package.resources.all():
            feed.append(a.entry(
                    a.title(resource.short_name),
                    a.id('http://%s%s' % (domain, resource.get_absolute_url())),
                    a.updated(feedgenerator.rfc3339_date(resource.last_updated)),
                    a.summary(resource.description),
                    a.author(a.name(resource.developer)),
                    a.content(
                        resource.open_search_description,
                        type='application/opensearchdescription+xml')))
        return feed
        
    def render(self, request):
        if isinstance(self.data, Package):
            feed = self.package_to_atom(request, self.data)
            return etree.tostring(feed, encoding='utf-8', pretty_print=True,
                                  xml_declaration=True)
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
                    AtomEmitter.package_to_atom(request, self.data), {}))
        return super(CustomJSONEmitter, self).render(request)


