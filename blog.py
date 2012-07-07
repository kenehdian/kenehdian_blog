###########################################  MAIN BLOG CODE ################################
# adding this comment for a git test

import basehandler
import logging
from datetime import datetime, timedelta 
from google.appengine.api import memcache
from google.appengine.ext import db
import json

    
class Blog(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now=True)
    createdby = db.StringProperty()
    
    def as_dict(self):
        d = {}
        d["subject"]=self.subject
        d["content"]=self.content
        d["created"]=self.created.strftime('%Y, %m, %d')
        d["last_modified"]=self.last_modified.strftime('%Y, %m, %d')
        d["createdby"]=self.createdby
        return d
 
class BlogUpdater():
    def flush_cache(self):
        memcache.flush_all()
    
    def get_posts(self, update=False):
        posts,age = self.age_get("blog_posts")
        logging.error("Trying memcache")
        if posts is None or update:
            logging.error("Not in memcache, hitting the DB")
            posts = db.GqlQuery('SELECT * FROM Blog ORDER BY created DESC limit 10')
            posts=list(posts)
            self.age_set("blog_posts",posts)
        return posts,age
    
    def get_post(self, post_id="0", update=False):
        key = db.Key.from_path('Blog',int(post_id))
        logging.error("Trying memcache")
        posts,age = self.age_get(repr(key))
        if posts is None or update:
            logging.error("Not in memcache, hitting the DB")
            posts = db.get(key)
            posts=[posts]
            self.age_set(repr(key),posts)
        return posts,age
    
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
        blog = BlogUpdater()
        blog.flush_cache()
        self.redirect("/blog")       

        
class BlogHandler(basehandler.BaseHandler):
    def render_blog(self,posts,agestr):
        self.render('blog.html', posts=posts, agestr=agestr, username=self.username)
        
    def get(self):
        blog = BlogUpdater()
        posts,age =blog.get_posts()
        if self.format =='json':
            full_json = [post.as_dict() for post in posts]
            return self.render_json(full_json)
        else:
            self.render_blog(posts,blog.age_str(age))
        
class PostHandler(basehandler.BaseHandler):
    def get(self,post_id):
        #self.write('entering post handler')
        #key = db.Key.from_path('Blog',int(post_id))
        #post=db.get(key)
        blog = BlogUpdater()
        posts,age =blog.get_post(post_id=post_id)
        if not posts:
            self.error(404)
            self.write(repr(post))
            return
        if self.format == 'html':
            self.render('blog_post.html',posts=posts,username=self.username, agestr=blog.age_str(age))
        else:
            self.render_json(post.as_dict())
           
class NewPostHandler(basehandler.BaseHandler):
    def render_newpost(self,template,subject="",content="",error=""):
        content=content.replace('/n','<br>')
        #msg="variables are %s , %s  , %s , %s " % (subject, content, error, self.username)
        #self.write(msg)
        return self.render(template,subject=subject,content=content,error=error,username=self.username)
        
    def get(self):
        #self.write('Entering new post Handler<br>')
        #uid = self.read_secure_cookie('user_id')
        #msg='uid is: %s <br>'% uid
        #self.write(msg)
        #if uid:
            #user=User.by_id(int(uid))

        if self.user:
            self.render_newpost('newpost.html')
        else:
            #self.write('couldnt get user from uid')
            self.redirect("/signup")

        """
        username_cookie_val=self.request.cookies.get("user_id")
        if username_cookie_val:
            cookie_val = self.check_secure(username_cookie_val)
            if cookie_val: 
                username=str(cookie_val)
                #msg="cookie succeded. Cookie_val is: %s" % username
                #self.write(msg)
                self.render_newpost('newpost.html', username=username)
            else:
                msg="cookie failed. Cookie value founds is: %s" % username_cookie_val
                self.write(msg)
        """        
        
    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")
        createdby = self.username
        
        if subject and content:
            a = Blog(subject = subject, content = content, createdby = createdby) 
            a.put()
            blog = BlogUpdater()
            blog.get_posts(update=True)
            blog.get_post(str(a.key().id()), update=True)
            self.redirect("/blog/%s" % str(a.key().id()))
        else:
            error = "You must enter both a title and content."
            self.render_newpost('newpost.html', subject, content, error)
            
class JsonBlogHandler(basehandler.BaseHandler):
    def render_json(self):
        posts = db.GqlQuery('SELECT * FROM Blog ORDER BY created DESC limit 10')
        list=[]
        for post in posts:
            pdict={}
            pdict["subject"]=post.subject
            pdict["created"]=post.created.strftime('%Y, %m, %d')
            pdict["content"]=post.content
            pdict["last_modified"]=post.last_modified.strftime('%Y, %m, %d')
            list.append(pdict)
        json_str=json.JSONEncoder().encode(list)
        self.write(json_str)
    
    def get(self):
        self.render_json()    
        
class JsonPostHandler(basehandler.BaseHandler):
    def render_json(self):
        post = db.GqlQuery('SELECT * FROM Blog ORDER BY created DESC limit 1')
        list=[]
        pdict={}
        pdict["subject"]=post.subject
        pdict["created"]=post.created.strftime('%Y, %m, %d')
        pdict["content"]=post.content
        pdict["last_modified"]=post.last_modified.strftime('%Y, %m, %d')
        list.append(pdict)
        json_str=json.JSONEncoder().encode(list)
        self.write(json_str)
    
    def get(self):
        self.render_json()    