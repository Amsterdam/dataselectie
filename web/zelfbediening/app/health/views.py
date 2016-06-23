from flask import Blueprint, request, render_template, flash, g

from app import db

mod = Blueprint('health', __name__, url_prefix='/status')

@mod.route('/reachable', methods=['GET', 'HEAD', 'OPTIONS'])
def status():
    return 'Ok', 200

