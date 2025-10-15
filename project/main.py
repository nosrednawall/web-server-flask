from flask import Blueprint, render_template
from flask_login import login_required, current_user
from .extensions import db

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)

@main.route('/sharepoint')
@login_required
def sharepoint():
    return render_template('sharepoint/index.html')

@main.route('/sap')
@login_required
def sap():
    return render_template('sap/index.html')

@main.route('/neogrid')
@login_required
def neogrid():
    return render_template('neogrid/index.html')
