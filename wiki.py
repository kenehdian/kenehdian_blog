#######################################  KEN-EH-DIAN-IPEDIA CODE #############
import basehandler
import logging
from datetime import datetime, timedelta 
from google.appengine.api import memcache
from google.appengine.ext import db
import json

    
class Wiki(db.Model):
    title = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now=True)
    createdby = db.StringProperty()
    
    def as_dict(self):
        d = {}
        d["title"]=self.subject
        d["content"]=self.content
        d["created"]=self.created.strftime('%Y, %m, %d')
        d["last_modified"]=self.last_modified.strftime('%Y, %m, %d')
        d["createdby"]=self.createdby
        return d
 
class WikiUpdater():
    def flush_cache(self):
        memcache.flush_all()
        
    def get_wikis(self, update=False):
        wikis = db.GqlQuery("SELECT * FROM Wiki ORDER BY title limit 100")
        return wikis
        
    def get_wiki(self, wiki_id=None, update=False):
        key = db.Key.from_path('Wiki',wiki_id)
        logging.error("Trying memcache")
        wiki,age = self.age_get(repr(key))
        if wiki is None or update:
            logging.error("Not in memcache, hitting the DB")
            wiki = db.get(key)
            self.age_set(repr(key),wiki)
        return wiki,age
    
    def age_set(self, key, value):
        savetime=datetime.utcnow()
        memcache.set(key,(value,savetime))
        
    def age_get(self, key):
        r=memcache.get(key)
        if r:
            val, savetime = r
            age = (datetime.utcnow() - savetime).total_seconds()
        else:
            val, age = None, 0
        return val, age
    
    def age_str(self, age):
        s = 'Queried %s seconds ago.'
        age = int(age)
        return s % age    

class FlushHandler(basehandler.BaseHandler):   
    def get(self):
        wiki = WikiUpdater()
        wiki.flush_cache()
        self.redirect("/wiki")       

class MainHandler(basehandler.BaseHandler):
    def get(self):
        update_wiki = WikiUpdater()
        wikis =update_wiki.get_wikis()
        wikis=list(wikis)
        if self.format == 'html':
            self.render('wiki.html',wikis=wikis,username=self.username, agestr="need to replace with age of cache")
        else:
            for wiki in wikis:
                self.render_json(wiki.as_dict())
 

        
class WikiHandler(basehandler.BaseHandler):
    def get(self,wiki_id):
        update_wiki = WikiUpdater()
        wiki,age =update_wiki.get_wiki(wiki_id=wiki_id)
        if not wiki:
            self.redirect("/wiki/_edit/%s" % wiki_id)
            return
        if self.format == 'html':
            self.render('wiki_page.html',wiki=wiki,username=self.username, agestr="replace with variable once working")
        else:
            self.render_json(wiki.as_dict())
           
class editWikiHandler(basehandler.BaseHandler):
    def render_new_wiki(self,template,title="",content="",error=""):
        content=content.replace('/n','<br>')
        #msg="variables are %s , %s  , %s , %s " % (title, content, error, self.username)
        #self.write(msg)
        return self.render(template,title=title,content=content,error=error,username=self.username)
        
    def get(self,wiki_id):
        if self.user:
            update_wiki = WikiUpdater()
            wiki,age=update_wiki.get_wiki(wiki_id=wiki_id)
            if wiki: 
                content=wiki.content 
            else: 
                content=""
            self.render_new_wiki('new_wiki.html',title=wiki_id, content=content)
        else:
            #self.write('couldnt get user from uid')
            self.redirect("/signup")  
        
    def post(self,wiki_id):
        title = wiki_id
        content = self.request.get("content")
        createdby = self.username
        
        if title and content:
            wiki = Wiki(key_name=title, title = title, content = content, createdby = createdby) 
            wiki.put()
            update_wiki = WikiUpdater()
            update_wiki.get_wiki(wiki_id=wiki_id, update=True)
            self.redirect("/wiki/%s" % wiki.key().name())
        else:
            error = "You must enter both a title and content."
            self.render_new_wiki('new_wiki.html', title, content, error)
            
class JsonWikiHandler(basehandler.BaseHandler):
    def render_json(self):
        wikis = db.GqlQuery('SELECT * FROM Wiki ORDER BY created DESC limit 100')
        list=[]
        for wiki in wikis:
            wdict={}
            wdict["title"]=wiki.title
            wdict["created"]=wiki.created.strftime('%Y, %m, %d')
            wdict["content"]=wiki.content
            wdict["last_modified"]=post.last_modified.strftime('%Y, %m, %d')
            list.append(wdict)
        json_str=json.JSONEncoder().encode(list)
        self.write(json_str)
    
    def get(self):
        self.render_json()    
