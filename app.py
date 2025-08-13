import os
import logging
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from extensions import db, mail

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET") or "neonexus36-default-secret-key"
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL") or "sqlite:///qrmealpass.db"
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# configure mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'teamneonexus@gmail.com'
app.config['MAIL_PASSWORD'] = "bmoh roil yjrw vzjz"
app.config['MAIL_DEFAULT_SENDER'] = 'teamneonexus@gmail.com'

# initialize extensions
db.init_app(app)
mail.init_app(app)

with app.app_context():
    # Import models to create tables
    import models  # noqa: F401
    db.create_all()

# Import and register routes
from routes import *  # noqa: F401, F403

if __name__ == '__main__':
    print(" * Access the application at http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
