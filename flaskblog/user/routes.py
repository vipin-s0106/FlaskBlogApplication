from flask import render_template,url_for,flash,redirect,request,Blueprint
from flaskblog.user.forms import RegistrationForm,LoginForm,UpdateAccountForm,ForgotPassword,ForgotPassword_OTP,ForgotPassword_Resend_OTP,Password_Change
from flaskblog import bcrypt
from functools import wraps
from Utils.ConfigReader import getInstance
from Utils.DBConnectivity import DBConnectivity
from flaskblog.user.utils import *
from Utils.GmailFactory import send_email
import random
from flaskblog import session
 
users = Blueprint('users',__name__)


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


@users.route('/register',methods=['GET','POST'])
@is_logged_off
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        username = form.username.data
        email = form.email.data
        query = "select * from user where username='"+username+"'"
        reader = getInstance()
        con = DBConnectivity.getConnection(reader.get('Credential', 'hostname'), reader.get('Credential', 'username'), reader.get('Credential', 'passwrod'), reader.get('Credential', 'database'))
        cursor = DBConnectivity.getQueryResult(con, query)
        cursor = cursor.fetchone()
        if(cursor == None):
            query = "select * from user where email='"+email+"'"
            cursor = DBConnectivity.getQueryResult(con, query)
            cursor = cursor.fetchone()
            if(cursor == None):
                query = "insert into user(username,email,password) values('"+username+"','"+email+"','"+hashed_password+"')"
                DBConnectivity.updateDatabase(con, query)
                flash(f"User has successfully registered!", "success")
                DBConnectivity.closeConnection(con)
                return redirect(url_for("users.login"))
            else:
                DBConnectivity.closeConnection(con)
                flash(f"Email has already exists!", "danger")
                return redirect(url_for("users.register"))
        else:
            DBConnectivity.closeConnection(con)
            flash(f"Username has already exists!", "danger")
            return redirect(url_for("users.register"))          
    return render_template("register.html",title = "Registration" , form = form)


@users.route('/login',methods=['GET','POST'])
@is_logged_off
def login():
    form = LoginForm()
    if form.validate_on_submit():
        reader = getInstance()
        con = DBConnectivity.getConnection(reader.get('Credential', 'hostname'), reader.get('Credential', 'username'), reader.get('Credential', 'passwrod'), reader.get('Credential', 'database'))
        query = "select * from user where Email='"+form.email.data+"'"
        cursor = DBConnectivity.getQueryResult(con, query)
        user = cursor.fetchone()
        if user != None:
            hashed_pwd = str(user[3])
            if(bcrypt.check_password_hash(hashed_pwd,form.password.data)):
                session['logged_in'] = True
                session['username'] = user[1]
                session['email'] = user[2]
                session['image_file'] = user[4]
                #flash("You have been logged in", "success")
                return redirect(url_for("users.account"))
            else:
                flash("Invalid Password!!", "danger")
                return redirect(url_for("users.login"))
            DBConnectivity.closeConnection(con)
        else:
            flash("User does not exists!", "danger")
            return redirect(url_for("users.register"))
        DBConnectivity.closeConnection(con)
    return render_template("login.html",title = "Login" , form = form)
 
 
@users.route('/account',methods=['GET','POST'])
@is_logged_in
def account():
    form=UpdateAccountForm()
    reader = getInstance()
    con = DBConnectivity.getConnection(reader.get('Credential', 'hostname'), reader.get('Credential', 'username'), reader.get('Credential', 'passwrod'), reader.get('Credential', 'database'))
    query = "select * from user where username='"+session['username']+"'"
    user = DBConnectivity.getQueryResult(con, query).fetchone()
    if form.validate_on_submit():
        query = "select * from user where username='"+form.username.data+"' and user_id <> "+str(user[0])
        result = DBConnectivity.getQueryResult(con, query).fetchone()
        if result == None:
            query = "select * from user where email='"+form.email.data+"' and user_id <> "+str(user[0])
            result = DBConnectivity.getQueryResult(con, query).fetchone()
            if result == None:
                if form.picture.data:
                    picture_file = save_picture(form.picture.data)
                    query = "UPDATE USER SET image_file='"+picture_file+"' where user_id="+str(user[0])
                    DBConnectivity.updateDatabase(con, query)
                    session['image_file'] = picture_file
                session['username'] = form.username.data
                session['email'] = form.email.data
                query = "UPDATE USER SET username='"+form.username.data+"',email='"+form.email.data+"' where user_id="+str(user[0])
                DBConnectivity.updateDatabase(con, query)
                DBConnectivity.closeConnection(con)
                flash("Account has been updated!","success")
                return redirect(url_for("users.account"))
            else:
                DBConnectivity.closeConnection(con)
                flash("Email has already exists!","danger")
                return redirect(url_for("users.account"))
        else:
            DBConnectivity.closeConnection(con)
            flash("Username has already exists!","danger")
            return redirect(url_for("users.account"))
        
    elif request.method == "GET":
        form.username.data = session['username']
        form.email.data = session['email'] 
    if(user[4] == None):
        image_file = url_for('static',filename = 'profilepics/pubg.jpg')
    else:
        image_file = url_for('static',filename = 'profilepics/'+user[4])
    DBConnectivity.closeConnection(con)
    return render_template('account.html',title ="Account",image_file=image_file,form=form)    
       
 
@users.route('/logout')
@is_logged_in
def logout():
    session.clear()
    return redirect(url_for("main.home"))


@users.route('/my_post')
@is_logged_in
def my_post():
    reader = getInstance()
    con = DBConnectivity.getConnection(reader.get('Credential', 'hostname'), reader.get('Credential', 'username'), reader.get('Credential', 'passwrod'), reader.get('Credential', 'database'))
    query = "select u.user_id,u.username,u.image_file,p.post_id,p.title,p.content,p.date_posted from user u join posts p on u.user_id=p.user_id where u.username='"+session['username']+"'"
    posts = DBConnectivity.getQueryResult(con, query).fetchall()
    return render_template("my_post.html",posts=posts)


@users.route('/forgot_password',methods=['GET','POST'])    
@is_logged_off
def forgot_password():
    form = ForgotPassword()
    if form.validate_on_submit():
        reader = getInstance()
        con = DBConnectivity.getConnection(reader.get('Credential', 'hostname'), reader.get('Credential', 'username'), reader.get('Credential', 'passwrod'), reader.get('Credential', 'database'))
        query = "select * from user where email='"+form.email.data+"'"
        result = DBConnectivity.getQueryResult(con, query).fetchone()
        if result != None:
            session['email'] = form.email.data
            OTP =  str(random.randrange(1001,10000))
            session['OTP'] = OTP
            subject = "Flask Blog Application"
            msg = OTP+"  is your One time password (OTP) for Flask Blog Application."
            send_email(subject, msg, form.email.data)
            flash("Email has been sent with OTP to given Email address","success")
            return redirect(url_for("users.forgot_password_otp"))
        else:
            flash("Email does not exists Please Sign Up","danger")
            return redirect(url_for("users.register"))
        DBConnectivity.closeConnection(con)
    return render_template('forgot_password.html',form=form)
   
 
@users.route('/forgot_password_otp',methods=['GET','POST'])    
@is_logged_off
def forgot_password_otp():
    form = ForgotPassword_OTP()
    if form.validate_on_submit():
        counter = form.otp_counter.data
        if (counter == '0'):
            session['OTP'] = None
            flash("OTP has been expired","danger")
            return redirect(url_for("users.forgot_password_otp_resend"))
        else:
            if session['OTP'] == form.otp.data:
                return redirect(url_for("users.forgot_password_change"))
            else:
                flash("OTP is incorrect","danger")
                return redirect(url_for("users.forgot_password_otp_resend"))
    elif request.method == 'GET':
        form.email.data = session['email']
    return render_template('forgot_password_otp.html',form=form)
   
@users.route('/forgot_password_otp_resend',methods=['GET','POST'])    
@is_logged_off
def forgot_password_otp_resend():
    form = ForgotPassword_Resend_OTP()
    if form.validate_on_submit():
        reader = getInstance()
        con = DBConnectivity.getConnection(reader.get('Credential', 'hostname'), reader.get('Credential', 'username'), reader.get('Credential', 'passwrod'), reader.get('Credential', 'database'))
        query = "select * from user where email='"+form.email.data+"'"
        result = DBConnectivity.getQueryResult(con, query).fetchone()
        if result != None:
            session['email'] = form.email.data
            OTP =  str(random.randrange(1001,10000))
            session['OTP'] = OTP
            subject = "Flask Blog Application"
            msg = OTP+"  is your One time password (OTP) for Flask Blog Application."
            send_email(subject, msg, form.email.data)
            return redirect(url_for("users.forgot_password_otp"))
        else:
            flash("Email Does not exists","danger")
            return redirect(url_for("users.register"))
        DBConnectivity.closeConnection(con)
    elif request.method == 'GET':
        form.email.data = session['email']
    return render_template('forgot_password_otp_resend.html',form=form)   

@users.route('/forgot_password_change',methods=['GET','POST'])    
@is_logged_off
def forgot_password_change():
    form = Password_Change()
    if form.validate_on_submit():
        reader = getInstance()
        con = DBConnectivity.getConnection(reader.get('Credential', 'hostname'), reader.get('Credential', 'username'), reader.get('Credential', 'passwrod'), reader.get('Credential', 'database'))
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        query = "update user set password='"+hashed_password+"' where email='"+session['email']+"'"
        DBConnectivity.updateDatabase(con, query)
        DBConnectivity.closeConnection(con)
        subject = "Flask Blog Application"
        msg = "Your password has been changed successfully!"
        send_email(subject, msg, session['email'])
        flash(msg, "success")
        return redirect(url_for("users.login"))
    return render_template('forgot_password_change.html',form=form)
  
