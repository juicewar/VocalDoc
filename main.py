from app import app, db
from models import DoctorUser, AdminUser
from email_handler import sendPasswordResetEmail, protectEmail
from flask import request, render_template, jsonify, flash, redirect, url_for
from forms import LoginForm, DoctorRegistrationForm, ResetPasswordForm, AdminRegistrationForm, DoctorCreateForm, ForgotPasswordForm
from speech_transcribe import transcribe_audio_file, convert_to_wav
from flask_login import current_user, login_user, logout_user, login_required, LoginManager, login_manager
import os
from forms import DoctorRegistrationForm

login = LoginManager(app)
login.login_view = 'login'

@login.user_loader
def load_user(user_id):
    return DoctorUser.query.get(user_id) or AdminUser.query.get(user_id)

@app.route('/')
def upload_file():
    if type(current_user) == AdminUser:
        return redirect(url_for('admin'))
    return render_template('index.html')

@app.route('/admin')
def admin():
    if type(current_user) == DoctorUser or current_user.is_anonymous:
        return redirect(url_for('upload_file'))
    return render_template('admin.html')

@app.route('/login', methods=['POST','GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('upload_file'))
    # print("login")
    form = LoginForm()
    if form.validate_on_submit():
        user = DoctorUser.query.filter_by(email=(form.email.data).lower()).first() or AdminUser.query.filter_by(username=(form.email.data).lower()).first()
        if user is None or not user.checkPassword(form.password.data):
            flash('Invalid username or password')
            return render_template('login.html', form=form, message="Invalid credentials")
        login_user(user, remember=form.remember.data)
        if type(user) == DoctorUser:
            return redirect(url_for('upload_file'))
        else:
            return redirect(url_for('admin'))
    return render_template('login.html', form=form, message="Invalid credentials")

@app.route('/register', methods=['POST','GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('upload_file'))
    form = DoctorRegistrationForm()
    if form.validate_on_submit():
        #check database for details - is user pre-registered?
        #if so change to verified and send email confirmation
        x = DoctorUser.query.filter_by(idnumber=(form.idnumber.data),email=(form.email.data).lower(),dob=form.dob.data,verified=False).first()
        if x:
            with app.app_context():
                x.verified = True
                x.forename = form.forename.data
                x.surname = form.surname.data
                db.session.commit()
            sendPasswordResetEmail(x)
            # print(x.verified, x.forename, x.surname)
            db.session.commit()
            return render_template('credentials.html',valid=True, email=protectEmail(x.email))
        #else send message asking the user to contact the admin at place of work
        return render_template('credentials.html', valid=False)
    return render_template('registration.html', form=form)

@app.route('/resetpassword/<token>', methods=['POST','GET'])
def resetpassword(token):
    user = DoctorUser.verify_reset_password_token(token)
    if user is None:
        return render_template('reset_password.html', valid=False)
    form = ResetPasswordForm()
    if form.validate_on_submit():
        #check if password has changed
        if user.checkPassword(form.password.data)==False:
            with app.app_context():
                user.setPassword(form.password.data)
                user.passwordSet = True
                db.session.commit()
                flash('Your new password has been set.')
            db.session.commit()    
            return redirect(url_for('login'))
        else:
            flash('Password has not been changed.')
    return render_template('set_password.html', form=form, token=token, idnumber=user.idnumber, email=protectEmail(user.email), name=user.forename + " " + user.surname)
        
@app.route('/admin/register', methods=['POST','GET'])
def adminregister():
    if current_user.is_authenticated:
        return redirect(url_for('upload_file'))
    form = AdminRegistrationForm()
    if form.validate_on_submit():
        #check database for details - is user pre-registered?
        #if so change to verified and send email confirmation
        x = AdminUser.query.filter_by(username=(form.username.data).lower()).first()
        if x is None:
            x = AdminUser()
            x.username = (form.username.data).lower()
            x.setPassword(form.password.data)
            with app.app_context():
                db.create_all()
                db.session.add(x)
                db.session.commit()
            db.session.commit()
            return redirect(url_for('login'))
        else:
            flash(f'Admin {form.username.data} already exists.')
        #else send message asking the user to contact the admin at place of work
    return render_template('registration_admin.html', form=form)

@app.route('/admin/create', methods=['POST','GET'])
def createdoctor():
    if type(current_user) == DoctorUser or current_user.is_anonymous:
        return redirect(url_for('upload_file'))
    if current_user.is_authenticated:
        form = DoctorCreateForm()
        if form.validate_on_submit():
            x = DoctorUser.query.filter_by(idnumber=(form.idnumber.data)).first() or DoctorUser.query.filter_by(email=(form.email.data).lower()).first()
            if x is None:
                x = DoctorUser()
                x.email = (form.email.data).lower()
                x.idnumber = form.idnumber.data
                x.dob = form.dob.data
                with app.app_context():
                    db.create_all()
                    db.session.add(x)
                    db.session.commit()
                db.session.commit()
                flash(f'New Doctor (id {form.idnumber.data}) has been created.')
                return redirect(url_for('admin'))
            else:
                flash(f'Doctor (id {form.idnumber.data}) already exists.')
        return render_template('create_doctor.html', form=form)
    
@app.route('/uploader', methods=['POST'])
def uploader():
    if 'file' not in request.files:
        return 'No file part'

    file = request.files['file']
    if file.filename == '':
        return 'No selected file'

    # Valid file
    if file:
        filename = "temp.wav"

        # Save the file locally
        saved_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(saved_path)
        convert_to_wav(saved_path)

        # Process the file
        transcribed_speech = transcribe_audio_file(saved_path)
        return jsonify({'message': transcribed_speech})

@app.route('/recordings', methods=['POST','GET'])
def recordings():
    #get all previous transcriptions
    return render_template('recordings.html')

@app.route('/forgotpassword', methods=['POST','GET'])
def forgotpassword():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = DoctorUser.query.filter_by(email=(form.email.data).lower()).first()
        if user is None:
            return render_template('credentials.html', valid=False)
        sendPasswordResetEmail(user)
        return render_template('credentials.html', valid=True, email = protectEmail(form.email.data))
    return render_template('forgot_password.html', form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('upload_file'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)         