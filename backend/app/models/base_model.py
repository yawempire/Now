from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Enum
db = SQLAlchemy()

Base = declarative_base()

class BaseModel(db.Model):
    __abstract__ = True  # Indicates that this class should not be created as a table
    #id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def save(self):
        """Save the object to the database."""
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """Delete the object from the database."""
        db.session.delete(self)
        db.session.commit()
