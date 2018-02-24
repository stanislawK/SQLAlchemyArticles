from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
db = SQLAlchemy()


class Articles(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    content = db.Column(db.Text()) #w przypadku długiego tekstu, string zajmuje zawsze miejsce w tabeli, text nie zajmuje miejsa w samej tabeli
    author = db.Column(db.String(30), nullable=False)
    created = db.Column(db.DateTime(), nullable=False, default=datetime.utcnow)

    #dzięki temu jeśli urzyjemy printów wyprintuje nam zawartość, a nie tylko adres
    def __repr__(self):
        return "Articles(id={}, title='{}', author='{}'".format(self.id, self.title, self.author)

class Users(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(130), nullable=False)
    username = db.Column(db.String(130), nullable=False, unique=True)
    email = db.Column(db.String(130), unique=True)
    password = db.Column(db.String(200), default='')
    register_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
