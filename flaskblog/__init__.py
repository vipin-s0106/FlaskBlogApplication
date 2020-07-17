from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask import session

app = Flask(__name__)
app.config['SECRET_KEY'] = '125a172d79899a122269f137c78485b0'
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)


from flaskblog.user.routes import users
from flaskblog.post.routes import posts
from flaskblog.main.routes import main
from flaskblog.errors.handlers import errors

app.register_blueprint(users)
app.register_blueprint(posts)
app.register_blueprint(main)
app.register_blueprint(errors)


