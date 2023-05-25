"""Routes for users blueprint."""

from flask import Flask, Blueprint

root_views = Blueprint('user_views', __name__)

from sqlalchemy.exc import IntegrityError

