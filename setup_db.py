from datetime import datetime

from app import app, db
from models import Users

app.app_context().push()

#poniższ linijka tworzy bazę danych
db.create_all()

#usuwanie wszystkich użytwkowników
# users = Users.query.all()
# for user in users:
#     db.session.delete(user)
# db.session.commit()

# #dopiero po wykonaniu linijki commit dodajemy do bazy danych, wcześniej treść jest tylko w pamięci podręcznej
# db.session.commit()