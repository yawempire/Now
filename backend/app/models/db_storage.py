from flask_sqlalchemy import SQLAlchemy
from flask import current_app, Flask
from .base_model import BaseModel 
# Ensure this is your declarative base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine

# Initialize SQLAlchemy with no settings
db = SQLAlchemy()

class DBStorage:
    """Interacts with the database using Flask-SQLAlchemy"""
    __engine = None
    __session = None

    def __init__(self, db):
        self.db = db
    
    def all(self, cls=None):
        """Query on the current database session"""
        new_dict = {}
        if cls:
            objs = db.session.query(cls).all()
            for obj in objs:
                key = f'{obj.__class__.__name__}.{obj.id}'
                new_dict[key] = obj
        else:
            for cls in db.Model.__subclasses__():
                if hasattr(cls, '__tablename__'):
                    objs = db.session.query(cls).all()
                    for obj in objs:
                        key = obj.__class__.__name__ + '.' + str(obj.id)
                        new_dict[key] = obj
        return new_dict

    def alli(self, cls=None):
        """Query on the current database session"""
        new_dict = {}
        if cls:
            objs = db.session.query(cls).all()
            for obj in objs:
                key = obj.__class__.__name__ + '.' + obj.id
                new_dict[key] = obj
        else:
            for cls in db.Model._decl_class_registry.values():
                if hasattr(cls, '__tablename__'):
                    objs = db.session.query(cls).all()
                    for obj in objs:
                        key = obj.__class__.__name__ + '.' + (obj.id)
                        new_dict[key] = obj
        return new_dict

    def new(self, obj):
        """Add the object to the current database session"""
        db.session.add(obj)

    def save(self):
        """Commit all changes of the current database session"""
        db.session.commit()

    def query(self, cls):
        """-----------------"""
        return self.db.session.query(cls)

    def delete(self, obj=None):
        """Delete from the current database session obj if not None"""
        if obj is not None:
            db.session.delete(obj)

    def get(self, cls, id):
        """ GETS obj from DB by if"""
        return self.db.session.query(cls).get(id)

    def reload(self):
        """Reloads data from the database"""
        db.create_all()
    
    def to_dict(self, save_fs=None):
        """returns a dictionary containing all keys/values of the instance"""
        new_dict = self.__dict__.copy()
        if "created_at" in new_dict:
            new_dict["created_at"] = new_dict["created_at"].strftime(time)
        if "updated_at" in new_dict:
            new_dict["updated_at"] = new_dict["updated_at"].strftime(time)
        new_dict["__class__"] = self.__class__.__name__
        if "_sa_instance_state" in new_dict:
            del new_dict["_sa_instance_state"]
        if save_fs is None:
            if "password" in new_dict:
                del new_dict["password"]
        return new_dict

    def close(self):
        """Call remove() method on the private session attribute"""
        db.session.remove()
