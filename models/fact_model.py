from models.base_model import *
from peewee import CharField, BooleanField, TextField, DateTimeField, ForeignKeyField

from datetime import datetime


class User(BaseModel):
    name = CharField(40)
    password = CharField(250)


class FactModel(BaseModel):
    user = ForeignKeyField(User, related_name="facts")
    fact = TextField(20)
    is_true = BooleanField()
    timestamp = DateTimeField(default=datetime.now)
