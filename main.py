from flask import Flask, request,redirect,render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:buildablog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer , String

class Blog(db.Model):
    id = Column(Integer , primary_key = True)
    title = Column(String(120)) 
    body = Column(String(120))

    def __init__(self,title,body):
        self.title = title
        self.body = body


@app.route("/newpost",methods = ['GET'])
def main():  
    return render_template('newpost.html')



@app.route("/blog",methods = ['POST','GET'])
def blog():
    
    #if post request, i.e. user wants to save something
    if request.method == "POST":
        title = request.form['name']
        body = request.form['blog']

        #if we have errors, display them, otherwise redirect to individual
        if (body=='' and title ==''):
            error_1 = 'please fill the title of your blog'
            error_2 = 'please fill the body of your blog'
            return render_template('newpost.html',body_error = error_2, title_error = error_1)
        else:
            blog_post = Blog(title, body)
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

    #if get request and use wants to see all items   
    else:
        blogs = Blog.query.all()
        return render_template('blog.html', blogs=blogs)


if __name__ == '__main__':
    app.run()

