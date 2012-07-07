from google.appengine.ext import db
from google.appengine.api import memcache
import basehandler
import logging
import urllib2
import xml.dom.minidom as minidom

#################################### ASCII ART WEBPAGES #############################
GMAPS_URL = "http://maps.googleapis.com/maps/api/staticmap?size=380x263&sensor=false&"    
IP_URL="http://api.hostip.info?ip="
art_key = db.Key.from_path('ASCIIchan','arts')

class Art(db.Model):
    subject = db.StringProperty(required = True)
    art = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now=True)
    coord = db.GeoPtProperty()
    
        

class AsciiHandler(basehandler.BaseHandler):

    def render_asciiart(self,subject="",art="",error=""):
        #arts = db.GqlQuery("SELECT * FROM Art ORDER BY created DESC")
        #arts is a cursor or generator type funciton.  We should convert it to a list to avoid re-running the query to iterate over the list.
        arts = self.top_arts()
        arts = list(arts)
        points=filter(None, (a.coord for a in arts))
        img_url=None
        if points:
            img_url=self.gmaps_img(points)
        #self.write("Google maps url is: ")
        #self.write(img_url)
        self.render('asciiart.html',subject=subject,art=art,error=error,arts=arts,img_url=img_url)

    def top_arts(self, update = False):
        key = "top"
        arts = memcache.get(key)
        logging.error("tryin memcache")
        if arts is None or update:
            logging.error("hitting the DB")
            arts = db.GqlQuery("SELECT * FROM Art ORDER BY created DESC")
        arts = list(arts)
        memcache.set(key,arts)
        return arts
        
                
    def gmaps_img(self, points):
        markers = '&'.join('markers=%s,%s' % (p.lat, p.lon) for p in points)
        return GMAPS_URL+markers

    def get_coords(self, ip='4.2.2.2'):
        #ip='4.2.3.2'
        url = IP_URL + ip
        content = None
        try:
            content = urllib2.urlopen(url).read()
        except URLError:
            return
        if content:
            p=minidom.parseString(content)
            self.write(repr(p))
            elements =p.getElementsByTagName("gml:coordinates")
            self.write("elements")
            self.write(repr(elements))
            if elements: 
                nodeVal = elements[0].childNodes[0].nodeValue
                long, lat = nodeVal.split(",")
                return db.GeoPt(lat,long)
    
    def get(self):
        #self.write(repr(self.get_coords(self.request.remote_addr)))
        self.render_asciiart()
    def post(self):
        subject = self.request.get("subject")
        art = self.request.get("art")
        if subject and art:
            coord = self.get_coords(self.request.remote_addr)
            self.write(repr(coord))
            a = Art(subject=subject,art=art)
            if coord:
                a.coord=coord
            a.put()
            #self.write(["thanks for posting about ",str(subject)])
            self.redirect("/ascii/")
        else:
            error = "you must enter both a subject and artwork"
            self.render_asciiart(subject,art,error)
            