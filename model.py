
## implement orm
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

## lets define the tables

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String, unique = True, nullable = False)
    password = db.Column(db.String, nullable = False)
    isAdmin = db.Column(db.Boolean, default = False)
    isInfluencer = db.Column(db.Boolean, default = False)
    isSponsor = db.Column(db.Boolean, default = False)
