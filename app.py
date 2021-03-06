from flask import Flask, redirect, url_for, render_template, request, session
import sqlite3
import datetime
import unicodedata

# Functions
from databases import query


app = Flask(__name__)
conn = sqlite3.connect("users.db")
c = conn.cursor()


@app.route('/')
def home():
    posts = query.getAllPosts()
    if 'user' in session:
        n=session['user']
        return render_template('home.html', posts=posts, n=n)
    return render_template('home.html', posts=posts)

@app.route('/@<username>')
def profile(username):
    user = query.getUser(username)
    posts = query.getPostsForUser(username)
    if 'user' in session:
        n=session['user']
    else:
        return render_template('profile.html', user=user, posts=posts)
    if user:
        return render_template('profile.html', user=user, posts=posts, n=n) #n is not defined when user is not logged in
    else:
        return render_template('error.html',n=n)


@app.route('/@<username>/<slug>', methods=['GET','POST'])
def read(username, slug):
    if 'user' in session:
        n = session['user']
    post = query.getPost(username, slug)
    user = query.getUser(username)
    
    if user and post:
        if request.method=='POST':
            query.newComment(username,slug,request.form['text'],session['user'])
        comments = query.getComments(username, slug)
        print comments
        return render_template('post.html', n=n, post=post, user=user, comments=comments)
    else:
        return render_template('error.html')


@app.route('/@<username>/<slug>/comments', methods=['POST'])
def comment(username, slug):
    cusername = request.form['username']
    body = request.form['body']

    if query.newComment(username, slug, body, cusername):
        return redirect('/%s/%s' % username, slug)
    else:
        return render_template('error.html', error='comment creation failed')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['Username']
        password = request.form['Password']
        
        if query.confirmLogin(username, password):
            session['user'] = username
            return redirect('/@%s' % username)
    
        return render_template('login.html', error="Username and Password Incorrect")
    
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']
        first = request.form['first']
        last = request.form['last']

        if query.registerUser(first, last, username, password):
            session['user'] = username
            n=session['user']
            return redirect('/new')
        else:
            return render_template('signup.html', error="There was a problem signing up try again")
    else:
        return render_template('signup.html')


@app.route('/new', methods=['GET', 'POST'])
def new():
    if 'user' in session:
        n=session['user']
        if request.method == 'POST':
            title = request.form['title']
            body = request.form['text']
            username = session['user']
            if query.newPost(username, title, body):
                return redirect('/@%s' % (username))
            else:
                return render_template('error.html')
        else:
            return render_template('new.html', n=n)
    return redirect('/login')

@app.route('/about')
def about():
    if 'user' in session:
        n=session['user']
        return render_template('about.html', n=n)
    return render_template('about.html')

@app.route('/profile')
def prof():
    if 'user' in session:
        n=session['user']
        return redirect('/@%s' % session['user'])
    return redirect('/login')

@app.route('/logout')
def logout():
    session.clear();
    return redirect('/login')


if __name__ == '__main__':
    app.debug=True
    app.secret_key="Don't store this on github"
    app.run(host='0.0.0.0', port=8000)
