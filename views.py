from datetime import datetime

from flask import Flask, render_template, redirect, Blueprint, request, url_for, flash, session, logging, current_app
from sqlalchemy import desc
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from models import Articles, Users, db
from functools import wraps

#zamiast app, używamy blog, żeby nie było problemów z importami
blog = Blueprint('blog', __name__)

#przekierownie na adres posts
@blog.route('/', methods=['GET'])
def index():
    return render_template('home.html')

@blog.route('/about')
def about():
    return render_template('about.html')

@blog.route('/articles')
def articles():
    articles = Articles.query.order_by(desc(Articles.created))
    if articles:
        return render_template('articles.html', articles=articles)
    else:
        msg = 'No articles found'
        return render_template('articles.html', msg=msg)


#single article
@blog.route('/article/<int:id>')
def article(id):
    one_article = Articles.query.get(id)
    return render_template('article.html', one_article=one_article)

#Register form class
class RegisterForm(Form):
    name = StringField('Name', [validators.length(min=1, max=50)])
    username = StringField('Username', [validators.length(min=4, max=30)])
    email = StringField('Email', [validators.length(min=6, max=40)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Password do not match')
    ])
    confirm = PasswordField('Confirm Password')

#user register
@blog.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        username = form.username.data
        email = form.email.data
        password = sha256_crypt.encrypt(str(form.password.data))
        new_user = Users(name=name, username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash('You are nowe registered and can log in', 'success')
        return redirect(url_for('blog.login'))
    return render_template('register.html', form=form)

#user login
@blog.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password_candidate = request.form.get('password')

        #get user by username
        user = db.session.query(Users).filter(Users.username == username).first()

        if user:
            password = user.password

            #compere passowrds
            if sha256_crypt.verify(password_candidate, password):
                #passed:
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                return redirect(url_for('blog.dashboard'))
            else:
                error = 'Password not matched'
                return render_template('login.html', error=error)
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')

#check if user logged in - nie pozwala wejść ręcznie w dashboard jeśli nie jesteśmy zalogowani (przez wpisanie w adres)
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, please login', 'danger')
            return redirect(url_for('blog.login'))
    return wrap

#logout
@blog.route('/logout')
@is_logged_in #możemy to wspisać dzięki wrap, zabrania dostępu przez wpisanie adresu ręcznie
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('blog.login'))

#Dashboard
@blog.route('/dashboard')
@is_logged_in #możemy to wspisać dzięki wrap, zabrania dostępu przez wpisanie adresu ręcznie
def dashboard():
    articles = Articles.query.order_by(desc(Articles.created))
    if articles:
        return render_template('dashboard.html', articles=articles)
    else:
        msg = 'No articles found'
        return render_template('dashboard.html', msg=msg)

#Add article form class
class ArticleForm(Form):
    title = StringField('Title', [validators.length(min=1, max=200)])
    content = TextAreaField('Content', [validators.length(min=20)])

#Add Article
@blog.route('/add_article', methods=['GET', 'POST'])
@is_logged_in #możemy to wspisać dzięki wrap, zabrania dostępu przez wpisanie adresu ręcznie
def add_article():
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        content = form.content.data
        author = session['username']
        new_article = Articles(title=title, content=content, author=author)
        db.session.add(new_article)
        db.session.commit()
        flash('Article created', 'success')
        return redirect(url_for('blog.dashboard'))
    return render_template('add_article.html', form=form)

#Edit Article
@blog.route('/edit_article/<int:id>', methods=['GET', 'POST'])
@is_logged_in #możemy to wspisać dzięki wrap, zabrania dostępu przez wpisanie adresu ręcznie
def edit_article(id):
    one_article = Articles.query.get(id)

    #get form
    form = ArticleForm(request.form)

    #Populate article form fields
    form.title.data = one_article.title
    form.content.data = one_article.content

    if request.method == 'POST' and form.validate():
        title = request.form['title']
        content = request.form['content']
        one_article.title = title
        one_article.content = content
        db.session.commit()
        flash('Article updated', 'success')
        return redirect(url_for('blog.dashboard'))
    return render_template('edit_article.html', form=form)

#Delete article
@blog.route('/delete_article/<int:id>', methods=['GET', 'POST'])
@is_logged_in
def delete_article(id):
    one_article = Articles.query.get(id)
    db.session.delete(one_article)
    db.session.commit()
    flash('Article deleted', 'success')
    return redirect(url_for('blog.dashboard'))