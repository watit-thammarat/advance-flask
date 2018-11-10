from requests import Response
from flask import request, url_for

from db import db
from lib.mailgun import Mailgun
from .confirmation import ConfirmationModel

MAILGUN_DOMAIN = "sandbox3669868273aa47cfa7a7086d6d45eb1e.mailgun.org"
MAILGUN_API_KEY = "f984eae0d320458b684ba1044d3a5b63-4412457b-f285c485"
FROM_TITLE = "Stores REST API"
FROM_EMAIL = "postmaster@sandbox3669868273aa47cfa7a7086d6d45eb1e.mailgun.org"


class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), nullable=False, unique=True)
    confirmation = db.relationship(
        "ConfirmationModel", lazy="dynamic", cascade="all, delete-orphan"
    )

    @property
    def most_recent_confirmation(self) -> "ConfirmationModel":
        return self.confirmation.order_by(db.desc(ConfirmationModel.expire_at)).first()

    @classmethod
    def find_by_username(cls, username: str) -> "UserModel":
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_email(cls, email: str) -> "UserModel":
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_by_id(cls, _id: int) -> "UserModel":
        return cls.query.filter_by(id=_id).first()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()

    def send_confirmation_email(self) -> Response:
        link = f'{request.url_root[:-1]}{url_for("confirmation", confirmation_id=self.most_recent_confirmation.id)}'
        return Mailgun.send_confirmation_email(
            [self.email],
            "Registration confirmation",
            f"Please clik the link to confirm your registration {link}",
            f'<html><body>Please clik the link to confirm your registration <a href="{link}">link</a></body></html>',
        )
