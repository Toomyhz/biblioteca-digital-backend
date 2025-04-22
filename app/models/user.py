from app import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.column(db.Integer, primary_key=True)
    email = db.column(db.String(120), unique=True, nullable=False)