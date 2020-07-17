from flaskblog import session
from flask import render_template,Blueprint
from Utils.ConfigReader import getInstance
from Utils.DBConnectivity import DBConnectivity
main = Blueprint('main',__name__)

#******************************** Home Page **************************

@main.route('/')
@main.route('/home')
def home():
    reader = getInstance()
    con = DBConnectivity.getConnection(reader.get('Credential', 'hostname'), reader.get('Credential', 'username'), reader.get('Credential', 'passwrod'), reader.get('Credential', 'database'))
    query = "select u.user_id,u.username,u.image_file,p.post_id,p.title,p.content,p.date_posted from user u join posts p on u.user_id=p.user_id"
    posts = DBConnectivity.getQueryResult(con, query).fetchall()
    return render_template("home.html",posts=posts)

#********************************* About Page ***********************

@main.route('/about')
def about():
    return render_template("about.html")



