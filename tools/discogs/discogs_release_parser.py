#!/usr/bin/python

import hashlib
import sys
import os
import xml.sax
import xml.sax.handler
from xml.sax.saxutils import escape, quoteattr

class DiscogsHandler(xml.sax.handler.ContentHandler):
    def __init__(self):
        self.tree = []
        self.string = ""
        self.id = ""
        self.count = 0
        self.artists = []
        self.masters = []
        self.labels = []
        self.artist = ""
        self.master = ""
        self.content = ""
        self.dead_artists = []

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

        # Store release ID
        if len(self.tree) == 2 and attrs.get('id', False) and name == "release":
            self.id = attrs.getValue("id")

        # Store label IDs
        if name == "label" and attrs.get('name', False):
            self.labels.append(attrs.getValue("name"))

    def getArtistData(self, artist_id):
        if artist_id in self.dead_artists:
            return None
        else:
            try:
                with open("artists/" + artist_id) as f:
                    return f.read()
            except:
                print "Data for artist " + artist_id + " not found"
                self.dead_artists.append(artist_id)
                return None

    def endElement(self, name):
        self.tree.pop()

        # Create the closing tag
        self.string += escape(self.content) + "</" + name + ">"
        self.content = ""

        # Store the final artist ID
        if name == "artist" and self.artist != "":
            self.artists.append(self.artist)
            self.artist = ""

        # Store the final master ID
        if name == "master_id" and self.master != "":
            self.masters.append(self.master)
            self.master = ""

        if len(self.tree) == 1 and name == "release":
            if self.id != "" and os.path.exists("releases/" + self.id + ".xml"):
                print "Release " + self.id + " already done! :D"
            elif self.id != "":
                print "Doing release " + self.id
                relf = open("releases/" + self.id + ".xml", "w")
                relf.write("<discogs>")
                relf.write(self.string.encode("utf-8"))

                for artist in set(self.artists):
                    artistData = self.getArtistData(artist)
                    if artistData is not None:
                        relf.write(artistData)

                for master in set(self.masters):
                    filename = "masters/" + master
                    try:
                        f = open(filename)
                        relf.write(f.read())
                        f.close()
                    except:
                        print "Data for master " + master + " not found"

                for label in set(self.labels):
                    filename = "labels/" + hashlib.md5(label.encode("utf-8")).hexdigest()
                    try:
                        f = open(filename)
                        relf.write(f.read())
                        f.close()
                    except:
                        print "Data for label " + label.encode("utf-8") + " not found"

                relf.write("</discogs>")
                relf.close()
            else:
                print "No ID found D:"
                print self.string.encode("utf-8")

            self.string = ""
            self.id = ""
            self.artists = []
            self.masters = []
            self.labels = []

#            self.count = self.count + 1
#            if (self.count > 10000):
#                # FIXME: There must be a more appropriate exception to raise.
#                raise NameError("Reached maximum number of entries.")

    def characters(self, content):
        self.content += content

        # characters can contain partial information, so append to a string for now
        if self.tree[len(self.tree) - 1] == "master_id":
            self.master += content
        if self.tree[len(self.tree) - 1] == "id" and self.tree[len(self.tree) - 2] == "artist":
            self.artist += content

if not len(sys.argv) > 1:
    print "The date of the filenames should be provided as an argument."
    sys.exit()

print "Loading data for " + sys.argv[1]

filename = "discogs_" + sys.argv[1] + "_releases.xml"
print "Parsing release data from " + filename
try:
    xml.sax.parse(filename, DiscogsHandler())
except NameError:
    pass
