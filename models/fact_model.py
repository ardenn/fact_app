from models.base_model import *
from peewee import CharField, BooleanField, TextField, DateTimeField, ForeignKeyField

from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired

SECRET_KEY = os.environ.get("FLASK_SECRET_KEY")


class User(BaseModel):
    name = CharField(40)
    password = CharField(250)

    def generate_token(self, expiry=600):
        t = Serializer(secret_key=SECRET_KEY, expires_in=expiry)
        return t.dumps({"id": self.id})

    @staticmethod
    def verify_token(token):
        t = Serializer(SECRET_KEY)
        try:
            data = t.loads(token)
        except SignatureExpired:
            return None  # Token expired
        except BadSignature:
            return None  # Token Invalid
        user = User.get(User.id == data["id"])
        return user


class FactModel(BaseModel):
    user = ForeignKeyField(User, related_name="facts")
    fact = TextField(20)
    is_true = BooleanField()
    timestamp = DateTimeField(default=datetime.now)
