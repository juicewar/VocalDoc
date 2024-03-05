from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField, IntegerField, SelectField
from wtforms.validators import InputRequired, Length, Email, EqualTo, DataRequired

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(),Length(min=3,max=32),Email()])
    password = PasswordField('Password', validators=[InputRequired(),Length(min=8,max=80)])
    usertype = SelectField('Log in as:', choices=[('doctor','Doctor'),('admin','Admin')], default='doctor')
    remember = BooleanField('Remember me?')
    submit = SubmitField('Sign in')

class DoctorRegistrationForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(),Length(min=3,max=32),Email()])
    idnumber = IntegerField('Doctor ID Number', validators=[InputRequired()])
    forename = StringField('Forename',validators=[InputRequired()])
    surname = StringField('Surname',validators=[InputRequired()])
    dob = DateField('Date of birth',format='%Y-%m-%d',validators=[InputRequired()])
    submit = SubmitField('Register')

class AdminRegistrationForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(),Length(min=3,max=32),Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')