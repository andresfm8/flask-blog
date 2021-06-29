import os
from flask import Flask, make_response, request, redirect, render_template, send_from_directory
from dotenv import load_dotenv
#from firebase_admin import credentials, firestore, initialize_app
from datetime import datetime
import json

from flask.typing import StatusCode
from werkzeug.security import check_password_hash, generate_password_hash
from . import db
from app.db import get_db

load_dotenv()
app = Flask(__name__)
app.config['DATABASE'] = os.path.join(os.getcwd(), 'flask.sqlite')
db.init_app(app)

#Initialize Firestore DB
# firebase_creds = json.loads(os.getenv("FIREBASE_CREDS"))
# cred = credentials.Certificate(firebase_creds)
# default_app = initialize_app(cred)
# db = firestore.client()
# posts_ref = db.collection('posts')

@app.route('/')
def index():
    return render_template('index.html', url=os.getenv("URL"))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            return "Login Successful", 200 
        else:
            return error, 418
            
    return render_template('login.html', url=os.getenv("URL"))

@app.route('/register', methods=['GET', 'POST'])
def register():
    # try:
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = f"User {username} is already registered."

        if error is None:
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            db.commit()
            return f"User {username} created successfully"
        else:
            return error, 418
    return render_template('register.html', url=os.getenv("URL"))
    # except Exception as e:
    #     return f"An error Ocurred: {e}"

# @app.route('/add-blog-post', methods=['GET', 'POST'])
# def addBlogPost():
#     try: 
#         if request.method == 'POST':
#             postdata = dict(request.form)
#             new_post = {
#                 "title": postdata["title"],
#                 "content": postdata["content"],
#                 "date": datetime.now()
#             }
#             posts_ref.add(new_post)

#             return redirect(os.getenv("URL") + 'blog')
#         else:
#             return render_template('add-blog-post.html', url=os.getenv("URL"))
#     except (Exception) as e:
#         return f"An error Ocurred: {e}"

# @app.route('/blog', methods=['GET'])
# def blog():
#     try: 
#         all_posts = [doc.to_dict() for doc in posts_ref.stream()]
#         return render_template('blog.html', posts=all_posts, url=os.getenv("URL"))
#     except (Exception) as e:
#         return f"An error Ocurred: {e}"

@app.route('/health')
def health():
    try:
        res = app.response_class(
            response = "Successful request",
            status = 200,
            mimetype = 'application.json'
        )
        return make_response(res, 200)
    except (Exception) as e:
        return f"An error ocurre: {e}"
