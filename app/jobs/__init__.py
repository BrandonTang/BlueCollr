from flask import Blueprint

jobs = Blueprint('jobs', __name__)

from ..jobs import views, forms
