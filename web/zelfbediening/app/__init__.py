# Python
import os
import sys
# Packages
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('app.config')

db = SQLAlchemy(app)

# Registering blueprints
from app.health.views import mod as healthModule
app.register_blueprint(healthModule)

