from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,BooleanField,FileField
from wtforms.validators import DataRequired,Email,EqualTo,Length
from flask_wtf.file import FileAllowed


class RegistrationForm(FlaskForm):
    username = StringField('Username',validators = [DataRequired(),Length(min = 2 , max = 20)])
    email = StringField('Email',validators = [DataRequired(),Email()])
    password = PasswordField('Password',validators = [DataRequired()])
    confirm_password = PasswordField('Confirm Password',validators = [DataRequired(),EqualTo('password')])
    submit = SubmitField('Sign Up')

    
class LoginForm(FlaskForm):
    email = StringField('Email',validators = [DataRequired(),Email()])
    password = PasswordField('Password',validators = [DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
    
class UpdateAccountForm(FlaskForm):
    username = StringField('Username',validators = [DataRequired(),Length(min = 2 , max = 20)])
    email = StringField('Email',validators = [DataRequired(),Email()])
    picture = FileField('Update Profile Picture',validators=[FileAllowed(['jpg','png'])])
    submit = SubmitField('Update')
    
class ForgotPassword(FlaskForm):
    email = StringField('Email',validators = [DataRequired(),Email()])
    submit = SubmitField('Send OTP') 
    
class ForgotPassword_OTP(FlaskForm):
    email = StringField('Email',validators = [DataRequired(),Email()])
    otp = StringField('OTP',validators = [DataRequired(),Length(min = 1 , max = 6)])
    otp_counter = StringField()
    submit = SubmitField('Verify')
    
class ForgotPassword_Resend_OTP(FlaskForm):
    email = StringField('Email',validators = [DataRequired(),Email()])
    submit = SubmitField('ReSend OTP')
    
class Password_Change(FlaskForm):
    password = PasswordField('Password',validators = [DataRequired()])
    confirm_password = PasswordField('Confirm_Password',validators = [DataRequired(),EqualTo('password')])
    submit = SubmitField('Change Password')
    
    