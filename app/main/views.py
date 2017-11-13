from app import db
from ..main import main

from flask import render_template


@main.route('/')
def index():
    return render_template('index.html')
