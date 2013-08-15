#!/usr/bin/python

import hashlib
import xml.sax
import xml.sax.handler
import sys
from xml.sax.saxutils import escape, quoteattr

class DiscogsHandler(xml.sax.handler.ContentHandler):
    def __init__(self, entity):
        self.tree = []
        self.string = ""
        self.id = ""
        self.name = ""
        self.entity = entity
        self.count = 0
        self.content = ""

    def startElement(self, name, attrs):
        self.tree.append(name)

        # Ignore the top-level container, e.g. <releases>
        if len(self.tree) == 1:
            return

        # Create the opening tag and its attributes
        self.string += "<" + name
        for attr in attrs.getNames():
            self.string += " " + attr + "=" + quoteattr(attrs.getValue(attr))
        self.string += ">"

        # IDs for masters are an attribute of the <master> element
        if len(self.tree) == 2 and name == 'master' and attrs.get('id', False):
            self.id = attrs.getValue("id")

    def endElement(self, name):
        self.tree.pop()

        # Create the closing tag
        self.string += escape(self.content) + "</" + name + ">"
        self.content = ""

        if len(self.tree) == 1 and name == self.entity:
            if self.entity == "label" and self.name != "":
                filename = "labels/" + hashlib.md5(self.name.encode("utf-8")).hexdigest()
                f = open(filename, "w")
                f.write(self.string.encode("utf-8"))
                f.close()
            elif self.id != "":
                filename = self.entity + "s/" + self.id
                f = open(filename, "w")
                f.write(self.string.encode("utf-8"))
                f.close()
            else:
                print "No ID found D:"
                print self.string.encode("utf-8")

            # Reset variables
            self.string = ""
            self.id = ""
            self.name = ""

#            self.count = self.count + 1
#            if (self.count > 10000):
#                # FIXME: There must be a more appropriate exception to raise.
#                raise NameError("Reached maximum number of entries.")

    def characters(self, content):
        self.content += content

        # IDs for artists and labels are a sub-element of <artist> and <label>
        if len(self.tree) == 3 and self.tree[2] == "id" and self.tree[1] == "artist":
            self.id += content
        if len(self.tree) == 3 and self.tree[2] == "name" and self.tree[1] == "label":
            self.name += content

if not len(sys.argv) > 1:
    print "The date of the filenames should be provided as an argument."
    sys.exit()

print "Loading data for " + sys.argv[1]

for entity in ("artist", "label", "master"):
    filename = "discogs_" + sys.argv[1] + "_" + entity + "s.xml"
    print "Parsing " + entity + " data from " + filename
    try:
        xml.sax.parse(filename, DiscogsHandler(entity))
    except NameError:
        pass
