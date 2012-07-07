
import basehandler
import cgi

formtext=""
rot13webpage = """
    <h2>Enter some text to ROT13:</h2>
	<form method="post">
		<textarea name="text" style="height: 100px; width: 400px;">%(formtext)s</textarea>
		<br>
		<input type="submit">
    </form>
    """

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

class Rot13Handler(basehandler.BaseHandler):
    def get(self):
        #self.response.out.write(template_dir)
        #self.render("signup.html")
        self.write_form()
    def post(self):
        input=self.request.get("text")
        posttext = self.remove_html(self.convert(input))
        self.write_form(posttext)
        
    def write_form(self,formtext=""):
        self.response.out.write(rot13webpage%{"formtext":formtext})
        
    def convert(self,text):
        result = ""
        for char in text:
            char = str(char)
            if not char.isalpha():
                result = result + char
            else:
                if char.isupper():
                    base=ord("A")
                else:
                    base=ord("a")
                result = result + chr( ( (ord(char) - base + 13) % 26) + base)
        return result
                
    def remove_html(self,text):
        return cgi.escape(text, quote=True)
#        result = ""
#        dict = {"<":"&lt",">":"&gt","&":"&amp","\"":"&quot"}
#        for char in text:
#            if char in dict:
#                result = result + dict[char]
#            else:
#                result = result + char
#        return result
