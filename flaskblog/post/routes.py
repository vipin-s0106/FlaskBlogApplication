from flask import render_template,url_for,flash,redirect,request,abort,Blueprint
from functools import wraps
from Utils.ConfigReader import getInstance
from Utils.DBConnectivity import DBConnectivity
from flaskblog.post.forms import PostForm
from flaskblog import session

posts = Blueprint('posts',__name__)

#check User logged in or not
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args,**kwargs)
        else:
            flash("Unauthorized, Please Login", "danger")
            return redirect(url_for("users.login"))      
    return wrap

#check User logged off or not
def is_logged_off(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' not in session:
            return f(*args,**kwargs)
        else:
            flash("Unauthorized, Please Logout", "danger")
            return redirect(url_for("main.home"))      
    return wrap

@posts.route("/post/new",methods=['GET','POST'])
@is_logged_in
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        reader = getInstance()
        con = DBConnectivity.getConnection(reader.get('Credential', 'hostname'), reader.get('Credential', 'username'), reader.get('Credential', 'passwrod'), reader.get('Credential', 'database'))
        query = "select * from user where username='"+session['username']+"'"
        user = DBConnectivity.getQueryResult(con, query).fetchone()
        query = "insert into posts(title,content,user_id) values('"+form.title.data+"','"+form.content.data+"',"+str(user[0])+")"
        print(query)
        DBConnectivity.updateDatabase(con, query)
        flash('Your post has been created!','success')
        return redirect(url_for('main.home'))
    return render_template('create_post.html',title='New Post',legend="New Post",form=form)


@posts.route("/post/<int:post_id>",methods=['GET','POST'])
def post(post_id):
    reader = getInstance()
    con = DBConnectivity.getConnection(reader.get('Credential', 'hostname'), reader.get('Credential', 'username'), reader.get('Credential', 'passwrod'), reader.get('Credential', 'database'))
    query = "select u.user_id,u.username,u.image_file,p.post_id,p.title,p.content,p.date_posted from user u join posts p on u.user_id=p.user_id where post_id="+str(post_id)
    post = DBConnectivity.getQueryResult(con, query).fetchone()
    return render_template('post.html',title=post[4],post=post)


@posts.route("/post/<int:post_id>/update",methods=['GET','POST'])
@is_logged_in
def update_post(post_id):
    form = PostForm()
    reader = getInstance()
    con = DBConnectivity.getConnection(reader.get('Credential', 'hostname'), reader.get('Credential', 'username'), reader.get('Credential', 'passwrod'), reader.get('Credential', 'database'))
    query = "select u.user_id,u.username,u.image_file,p.post_id,p.title,p.content,p.date_posted from user u join posts p on u.user_id=p.user_id where post_id="+str(post_id)
    post = DBConnectivity.getQueryResult(con, query).fetchone()
    if post[1] != session['username']:
        abort(403)
    if form.validate_on_submit():
        query = "update posts set title='"+form.title.data+"', content='"+form.content.data+"' where post_id="+str(post[3])
        DBConnectivity.updateDatabase(con, query)
        flash("Post has been successfully updated!","success")
        return redirect(url_for("posts.post",post_id=post[3]))
    elif request.method == 'GET':
        form.title.data=post[4]
        form.content.data = post[5]
    return render_template('create_post.html',title=post[4],legend="Update Post",post=post,form=form)


@posts.route('/delete_post/<int:post_id>',methods=['GET','POST'])
@is_logged_in
def delete_post(post_id):
    reader = getInstance()
    con = DBConnectivity.getConnection(reader.get('Credential', 'hostname'), reader.get('Credential', 'username'), reader.get('Credential', 'passwrod'), reader.get('Credential', 'database'))
    query = "delete from posts where post_id="+str(post_id)
    DBConnectivity.updateDatabase(con, query)
    flash("Your post has been successfully deleted!", "success")
    return redirect(url_for('main.home'))

