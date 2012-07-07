###################################### USER ACCOUNT FUCTIONS AND DATABASE CODE ###########################################

from google.appengine.ext import db
import basehandler
import hashlib
import re
import random
from string import letters

######################################################  ADMINISTRATION / USER ACCOUNT FUNCTIONS ###########################################
RE_USER = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
RE_PWD = re.compile(r"^.{3,20}$")
RE_EMAIL  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
           
class SignupHandler(basehandler.BaseHandler):

    def valid_name(self,username):
       return username and RE_USER.match(username)
       
    def valid_password(self,password):
        return password and RE_PWD.match(password)
        
    def valid_email(self,email):
        return not email or RE_EMAIL.match(email)

    def escape_html(self,s):
        return cgi.escape(s,quote=True)

    #def render_newsignup(self,username="", pwd="", verify="", email="", nameerror="", pwderror="", verifyerror="", emailerror=""):
    #    return self.render("signup.html", username=username, pwd=pwd, verify=verify, email=email, nameerror=nameerror, pwderror=pwderror, verifyerror=verifyerror, emailerror=emailerror)
    def render_newsignup(self,**params):
        return self.render("signup.html", **params)
        
    def get(self):
        self.render_newsignup(username=self.username)
        
    def post(self):
        have_error = False
        username = self.request.get("username")
        v_username = self.valid_name(username)
        pwd = self.request.get("password")
        v_password = self.valid_password(pwd)
        verify = self.request.get("verify")
        email = self.request.get("email")
        v_email = self.valid_email(email)
        nameerror, pwderror, verifyerror, emailerror = "","","",""
        #params = dict(username=username, pwd=pwd, email=email, nameerror="", verifyerror="", emailerror="")
        if not v_username: 
            nameerror = "You must enter a valid username."
            have_error = True
        if not v_password:  
            pwderror = "You must enter a valid password."
            have_error = True
        if not verify==pwd: 
            verifyerror = "Verify password does not match original password."
            have_error = True
        if not v_email:
            emailerror = "You must enter a valid email."
            have_error = True
        if not have_error:
            #self.write([username,pwd,'this is a test'])
            if not email: email=""
            user=User.by_name(username)
            if user:
                nameerror="That username is already in our database.  Choose a different name"
                #self.render_newsignup(**params)
                self.render_newsignup(username=username, pwd=pwd, verify=verify, email=email, nameerror=nameerror, pwderror=pwderror, verifyerror=verifyerror, emailerror=emailerror)
            else:
                self.write("Username OK, attempting to REGISTER<br>")
                user=User.register(username,pwd,email)
                self.write("USER_REGISTERED <br>")
                if user: 
                    user.put()
                    #self.write("PUTTING USER IN DB, <br>")
                    #self.write(str(user.key().id()))
                    self.login(user)
                    msg="USER Logged in <br>"
                    self.write(msg)
                else:
                    self.write("no user found after registration<br>")

                #new_cookie_val = str(self.make_secure(username))
                #self.response.headers['Content-Type']="text/plain"
                #self.response.headers.add_header("Set-Cookie","username="+new_cookie_val)

                #user=User.by_name(user.username)
                #msg="succefully registered user %s" % user.username
                #self.write(msg)
                self.write('about to redirect to welcome <br>')
                self.redirect('/welcome')
        else:   
            self.render_newsignup(username=username, pwd=pwd, verify=verify, email=email, nameerror=nameerror, pwderror=pwderror, verifyerror=verifyerror, emailerror=emailerror)
            #self.render('signup.html',**params)
            #self.write(str(params))

class LogoutHandler(basehandler.BaseHandler):
      
    def get(self):
        #self.write("hitting the handler")
        self.logout()
        self.redirect("/")
            
class LoginHandler(basehandler.BaseHandler):
    def render_newlogin(self,**params):
        return self.render("login.html", **params)
        
    def get(self):
        #self.write("hitting the handler")
        self.render_newlogin(username=self.username)
        
    def post(self):
        username = self.request.get("username")
        pwd = self.request.get("password")
        error = ""
        u = User.login(username, pwd)
        if u:
            self.login(u)
            #self.write("login suceeded, redirecting to homepage<br>")
            self.redirect('/welcome')
        else:
            error = 'Invalid login.  Please re-enter your name and password.'
            self.render('login.html', error=error,username=self.username)
########################################  USER DATABASE FUNCTIONS ##############################
class User(db.Model):
    username = db.StringProperty(required = True)
    user_pwd_hash = db.TextProperty(required = True)
    email = db.StringProperty()

    @classmethod
    def make_salt(cls,length = 5):
        return ''.join(random.choice(letters) for x in xrange(length))
    
    @classmethod 
    def make_pwd_hash(cls, name, pwd, salt = None):
        if not salt:
            salt = cls.make_salt()
        h = hashlib.sha256(name + pwd + salt).hexdigest()
        return '%s,%s' % (salt, h)

    @classmethod
    def valid_pwd(cls,name, pwd, h):
        salt = h.split(',')[0]
        return h == cls.make_pwd_hash(name, pwd, salt)    

    @classmethod
    def by_name(cls,name):
        q="WHERE username='%s'" % name
        u=User.gql(q).get()
        #u=User.all().filter('username=',name).get()
        return u
    
    @classmethod
    def by_id(cls,user_id):
        return User.get_by_id(user_id)

    @classmethod
    def register(cls, name, pwd, email=None):
        pwd_hash = cls.make_pwd_hash(name,pwd)
        return User(username=name, user_pwd_hash=pwd_hash, email=email)
        
    @classmethod
    def login(cls, user, pwd):
        u=cls.by_name(user)
        if u and cls.valid_pwd(user,pwd,u.user_pwd_hash):
            return u
             