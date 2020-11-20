from flask import Flask
from flask_static_digest import FlaskStaticDigest

flask_static_digest = FlaskStaticDigest()

app = Flask(__name__, template_folder='./project/application/frontend/templates', static_folder='./project/application/frontend/static')
app.secret_key = "secret key"
flask_static_digest.init_app(app)




