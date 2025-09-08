

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from .models import db

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///reservation.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
migrate = Migrate(app, db)

# Context processor must be defined after app is created
@app.context_processor
def inject_user():
	from app.models import User
	user = None
	from flask import session
	if 'user_id' in session:
		user = User.query.get(session['user_id'])
	return dict(user=user, User=User)

from .routes import main
app.register_blueprint(main)
