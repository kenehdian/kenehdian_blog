#########################  BASE WEBAPP2 HANDLER CODE THAT MOST WEBPAGES INHERIT ##########
#                          INHERIT BASEHANDLER INTO YOUR WEBAPP2 APP                     #
import webapp2
import os
import hmac
import jinja2
import json

######################################### GLOBALS ########################################
secret='replace_this_with_secret_website_code'
jinja_env = jinja2.Environment(autoescape=True,
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))

######################################### HANDLERS #########################################
class BaseHandler(webapp2.RequestHandler):
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))
    
    def write(self, *args, **kw):
        self.response.out.write(*args, **kw)
    
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        #self.write(params)
        return t.render(params)
        
    def render_json(self, jsonCompatible):
        json_text=json.dumps(jsonCompatible)
        self.response.headers['Content-Type']='application/json; charset=UTF-8'
        self.write(json_text)
   
    def make_secure(self,val):
        return "%s|%s" % (val,hmac.new(secret,val).hexdigest())
        
    def check_secure(self,cookie_val):
        val=cookie_val.split("|")[0]
        if cookie_val==self.make_secure(val):
            return val
        else:
            return None
            
    def set_secure_cookie(self, name, val):
        cookie_val = self.make_secure(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))
          
    #def set_secure_cookie(self, name, val):
    #    cookie_val=self.make_secure(val)
    #    self.response.headers.add_header('Set-Cookie', name+'='+cookie_val+'; Path=/')
    
    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and self.check_secure(cookie_val)

    def login(self, user):
        id=user.key().id()
        msg ='login is setting cookie for %s <br>' % id
        self.write(msg)
        self.set_secure_cookie('user_id', str(id))


    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        if self.request.url.endswith(".json"):
            self.format='json'
        else:
            self.format='html'
        uid = self.read_secure_cookie('user_id')
        if uid: import userdb
        self.user = uid and userdb.User.by_id(int(uid))
        if self.user: self.username=self.user.username 
        else: self.username=""
   