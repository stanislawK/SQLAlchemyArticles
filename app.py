from flask import Flask, logging

from models import db
from views import blog

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqldemo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.register_blueprint(blog)

db.init_app(app)


if __name__ == '__main__':
    app.secret_key = '1234'
    app.run(debug=True)