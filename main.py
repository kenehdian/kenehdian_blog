#!/usr/bin/env python
#
#####################################################   MAIN WEBSITE CODE ###################################
import basehandler
import blog
import ascii_art
import userdb
import rot13
import wiki

import webapp2
import jinja2
import cgi

from google.appengine.ext import db
from google.appengine.api import memcache
#from google.appengine.api import users
import random
import hashlib
import hmac
import json
import urllib2
from xml.dom import minidom
import logging


########################################## GLOBALS #########################################################  

########################################## COMMON BASE CLASSES ###############################################     

def users_key(group = 'default'):
    return db.Key.from_path('users', group)

########################################## USER DB MODEL ###############################################    
   
#########################################BLOG WEBPAGES #########################################################
    
class MainHandler(basehandler.BaseHandler):
    def get(self):
        if self.format == 'json':
            self.redirect("/blog.json")
        else:
            self.render('homepage.html', title='Ken-eh-dian', content='',username=self.username)

class AboutHandler(basehandler.BaseHandler):
    def get(self):
        self.render('about.html', title='Ken-eh-dian', content='',username=self.username)
        

#########################################ADMINISTRATION WEBPAGES #########################################################
 
#################################### ASCII ART WEBPAGES #############################

 #################################### TEST STUFF #############################   
class TestHandler(basehandler.BaseHandler):
    def get(self):
        cookie_val='test12345'
        cookie_name='test_cookie'
        self.set_secure_cookie(cookie_name,cookie_val)
        if self.read_secure_cookie(cookie_name) == cookie_val:
            self.write('Test1:  passed make_secure, check_secure, set_secure_cookie read_secure_cookie<br>')
        else:
            self.write(self.read_secure_cookie(cookie_name))
            self.write('Test 1: failed secure cookie tests<br>')
        u = User(username ='testname', user_pwd_hash = User.make_pwd_hash('testname','testpwd'), email='test_email')
        u.put()
        u2=User.gql("WHERE username='testname'")[0]
        if u2:
            self.write('Test 2 passed:  put user in database and pulled it back out<br>')
            msg='ID: '+str(u2.key().id())+'Username: '+u2.username+'HASH: '+u2.user_pwd_hash+'Email: '+u2.email
            self.write(msg)
        else:
            self.write('Test 2 failed: couldnt find user in dB')
        q=User.gql("WHERE username='Jaberwocky'")
        for item in q:  
            self.write('counldnt find user')
        if q:
            msg='Test 3 failed ... should not have found test username=Jaberwocky'
            self.write(msg)
        else:
            msg='Test 3 passed.  Got None result for non-existent user'
        #self.login(u)
        #self.write('check cookies<be>')
        #self.set_secure_cookie('user_id', str(u.key().id()))
        #self.response.headers['Content-Type']="text/plain"
        #visits = 0
        #visits_cookie_val=self.request.cookies.get("visits")
        #if visits_cookie_val:
        #    cookie_val = self.check_secure(visits_cookie_val)
        #    if cookie_val: 
        #        visits=int(cookie_val)
        #visits += 1
        #new_cookie_val = self.make_secure(str(visits))
        #self.response.headers.add_header("Set-Cookie","visits="+new_cookie_val)
        #self.write("you have visited this page %s times." % visits) 
        #if visits > 20:
        #    self.write("you are awesome")
        #self.render('testpage.html') 

 
app = webapp2.WSGIApplication([('/(?:\.json)?', MainHandler),('/rot13', rot13.Rot13Handler),('/blog/?(?:\.json)?', blog.BlogHandler),('/ascii/', ascii_art.AsciiHandler),('/about', AboutHandler),('/welcome', blog.NewPostHandler),('/newpost|/blog/newpost', blog.NewPostHandler),('/blog/?([0-9]+)(?:\.json)?', blog.PostHandler),
                              ('/signup|/blog/signup|/wiki/signup', userdb.SignupHandler),('/login|/blog/login|/wiki/login', userdb.LoginHandler),('/logout|/blog/logout|/wiki/logout', userdb.LogoutHandler),('/blogjson', blog.JsonBlogHandler),('/blogj/?([0-9]+).json', blog.JsonPostHandler),('/flush|/blog/flush', blog.FlushHandler),('/wiki', wiki.MainHandler),
                              ('/wiki/flush', wiki.FlushHandler),('/wiki/_edit/(.+)', wiki.editWikiHandler),('/wiki/(.+)', wiki.WikiHandler),('/test.*', TestHandler)],debug=True)
