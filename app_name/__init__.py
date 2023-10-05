from flask import Flask
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import os

from . import config
from .dbConnection import ConnectDB
from .utilities import *

# =============================================== CONFIG ===============================================
app = Flask(__name__)
app.config['PRODUCT_ENVIRONMENT'] = config.PRODUCT_ENVIRONMENT

# App URL
app.config['BASE_URL'] = config.BASE_URL
app.config['FRONTEND_URL'] = os.getenv('FRONTEND_URL')
app.config['WEB_UTAMA_URL'] = os.getenv('WEB_UTAMA_URL')

# Config JWT 🔑
app.config['SECRET_KEY'] = config.JWT_SECRET_KEY
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = config.JWT_ACCESS_TOKEN_EXPIRES
jwt = JWTManager(app)

# Config Database migration 🔑
app.config.from_object(ConnectDB)
app.config['db'] = SQLAlchemy(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Config Folder upload here 📁
app.config['FOTO_USER'] = config.STATIC_FOLDER_PATH + "foto/user/"
app.config['FOTO_PORTOFOLIO'] = config.STATIC_FOLDER_PATH + "foto/portofolio/"
app.config['FOTO_EVENT'] = config.STATIC_FOLDER_PATH + "foto/event/"
app.config['SERTIFIKAT'] = config.STATIC_FOLDER_PATH + "pdf/sertifikat/"
app.config['TEMPLATE_SERTIFIKAT'] = config.STATIC_FOLDER_PATH + "template-sertifikat/"
app.config['FONTS'] = config.STATIC_FOLDER_PATH + "fonts/"

# Create Folder if doesn't exist 👮‍♀️
list_folder_to_create = [
	app.config['FOTO_USER'],
	app.config['FOTO_PORTOFOLIO'],
	app.config['FOTO_EVENT'],
	app.config['SERTIFIKAT'],
	app.config['TEMPLATE_SERTIFIKAT'],
	app.config['FONTS']
]

for x in list_folder_to_create:
	if os.path.exists(x) == False:
		os.makedirs(x)

# =============================================== DATABASE MODEL ===============================================
from .database import portofolioModel, adminModel, userModel, logModel, kategoriModel, eventModel, kehadiranModel, packageModel, linkModel, authModel

# =============================================== ROUTING ===============================================
@app.route('/')
def index():
	return 'Central AI | Backend Central Admin v1.0'

# =============================================== BLUEPRINT ===============================================
# import blueprint here 👇
from .routes.admin.controllers import admin
from .routes.user.controllers import user
from .routes.auth.controllers import auth
from .routes.portofolio.controllers import portofolio
from .routes.event.controllers import event
from .routes.kehadiran.controllers import kehadiran
from .routes.sertifikat.controllers import sertifikat
from .routes.packages.controllers import packages
from .routes.shortlink.controllers import links
from .routes.kategori.controllers import kategori

# limiter = Limiter(app, default_limits = ["30/minute"], key_func=get_remote_address)

@app.errorhandler(429)
def ratelimit_handler(e):
  return defined_error("You have exceeded your rate-limit",'To Many request', 429)

# register blueprint here 👇
app.register_blueprint(admin)
app.register_blueprint(user)
app.register_blueprint(auth)
app.register_blueprint(portofolio)
app.register_blueprint(event)
app.register_blueprint(kehadiran)
app.register_blueprint(sertifikat)
app.register_blueprint(packages)
app.register_blueprint(links)
app.register_blueprint(kategori)