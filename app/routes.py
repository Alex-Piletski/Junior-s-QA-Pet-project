from flask import Blueprint, render_template
from . import db

bp = Blueprint('main', __name__)

@bp.route('/')
def home():
    return render_template('index.html')

@bp.route('/ping')
def ping():
    return {'status': 'ok'}
