from flask import Flask, request,redirect,render_template,session,flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz123@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'mmmmmmmmmm'

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer , String

class Blog(db.Model):
    id = Column(Integer , primary_key = True)
    title = Column(String(120)) 
    body = Column(String(120))
    owner_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    def __init__(self,title,body,owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = Column(Integer , primary_key = True)
    username = Column(String(120) , unique=True)
    password = Column(String(120))
    blogs = db.relationship('Blog' , backref='owner')
    
    def __init__(self,username,password):
        self.username = username
        self.password = password
        
#@app.route("/",methods = ['GET'])
#def main():  
#   return render_template('home.html')
@app.before_request ##run this function before you start any request handler
def require_login():
    allowed_routes = ['login','signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        
        return redirect('/login')


@app.route("/newpost",methods = ['GET'])
def main():  
   return render_template('newpost.html')

@app.route("/login",methods = ['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form ['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] =username #session is dictionary, under the key password, add password.the next time I come i can see if I have seen that before
            flash("Logged in")
            print("Logged in")
            return redirect('/newpost')
        else:
            try:
                if not user.password == password:
                    flash("Password is incorrect","error")
            except AttributeError:
                flash("User doesn't exist","error")
    
    return render_template ('login.html') 
    

    
    

@app.route("/signup",methods=['POST','GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        if (   
       username == '' and password == '' and
       verify == '' 
        ):
       # user_name = request.form['username'] 
            error = 'This field is required'
            return render_template('signup.html' , blank_error = error,password_error = error , verify_error = error,user = username)
        #return redirect("/?error=" + error)
        #templates = jinja_env.get_template('welcome.html')
        if (username == '' and password == ''):
            error = 'This field is required'
            return render_template('signup.html' , blank_error = error,password_error = error,user = username)
        if (password == '' and verify == ''):
            error = 'This field is required'
            return render_template('signup.html' , password_error = error,verify_error = error ,user = username)
        if verify == '' and username == '':
            error = 'This field is required'
            return render_template('signup.html' , verify_error = error,blank_error = error,user = username)
        if username == '':
            error = 'This field is required'
            return render_template('signup.html' , blank_error = error,user = username)
        if password == '':
            error = 'This field is required'
            return render_template('signup.html' , password_error = error,user = username)
        if verify == '':
            error = 'This field is required'
            return render_template('signup.html' , verify_error = error,user = username)


        if (len(username) <= 3 or len(username) > 20 or " " in username) :
            error = 'username is not valid'
            return render_template('signup.html' , user_error = error,user = username)

        if (len(password) <= 3 or len(password) > 20) or " " in password:
            error = 'password is not valid'
            return render_template('signup.html' , pass_error = error,user = username)
        if password != verify:
            error = "please verify your password"
            return render_template('signup.html' , v_error = error,user = username)

        else:
            existing_user = User.query.filter_by(username=username).first()
            if not existing_user:
                new_user = User(username,password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] =username
            else:
                return "<h1>Duplicate user</h1>"
    return render_template ('newpost.html')
@app.route('/logout',methods = ['GET'])
def logout():
    del session['username']
    return redirect('/index')

@app.route('/index', methods = ['POST','GET'])
def index():
    users = User.query.with_entities(User.id, User.username).all()

    return render_template('index.html', users=users)

@app.route("/blog",methods = ['POST','GET'])
def blog():
    
    #if post request, i.e. user wants to save something
    if request.method == "POST":
        title = request.form['name']
        body = request.form['blog']
        owner = User.query.filter_by(username = session['username']).first()

        #if we have errors, display them, otherwise redirect to individual
        if (body=='' and title ==''):
            error_1 = 'please fill the title of your blog'
            error_2 = 'please fill the body of your blog'
            return render_template('newpost.html',body_error = error_2, title_error = error_1)
        else:

            blog_post = Blog(title, body, owner)
            db.session.add(blog_post)
            db.session.commit()
            id =blog_post.id
            #blogs = Blog.query.all()
            blog_post = Blog.query.get(id)

            return render_template('individual.html',blogs=blog_post) 

    #if get request and use wants to see one item   
    elif 'id' in request.args:
        id = request.args.get("id")
        blog_post = Blog.query.get(id)
        return render_template("individual.html", blogs=blog_post)
    
    #if get request and use wants to see one item   
    elif 'user' in request.args:
        id = request.args.get("userId")
        blog_posts = Blog.query.filter_by(owner_id=id)
        return render_template("individual.html", blogs=blog_posts)

    #if get request and use wants to see all items   
    else:
        blogs = Blog.query.all()
        return render_template('blog.html', blogs=blogs)


if __name__ == '__main__':
    app.run()

