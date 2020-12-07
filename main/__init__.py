from flask import Flask
from flask import request
from flask import render_template
from flask import url_for
from flask import redirect
from flask import flash
from flask import abort
from flask import session
from bson.objectid import ObjectId
from flask_pymongo import PyMongo
from datetime import datetime
from datetime import timedelta
from functools import wraps
import time
import math



app = Flask(__name__, template_folder="templates")
app.config["MONGO_URI"] = "mongodb://localhost:27017/lch_blog" 
app.config['SECRET_KEY'] = 'password5'
#10일동안 로그인 session정보유지
app.config['PERMANENT_SESSION_LIFETIME'] =timedelta(days=10)
mongo = PyMongo(app)


from .common import login_required
from .filter import format_datetime
from . import board
from . import member


app.register_blueprint(board.blueprint)
app.register_blueprint(member.blueprint)