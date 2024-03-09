from app import app, db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from time import time

class AdminUser(UserMixin, db.Model):
    admin_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, nullable=False)
    passwordHash = db.Column(db.String(128), nullable=False)

    def setPassword(self, password):
        self.passwordHash = generate_password_hash(password)
    
    def checkPassword(self, password):
        return check_password_hash(self.passwordHash,password)

    def get_id(self):
        return self.admin_id
    
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.admin_id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')
    
    @staticmethod
    #reset password key contained in email that is hashed for the id
    def verify_reset_password_token(token):
        try:
            admin_id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            print("\n failure")
            return
        return AdminUser.query.get(admin_id)

class DoctorUser(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(32), unique=True, nullable=False)
    idnumber = db.Column(db.Integer, unique=True, nullable=False)
    forename = db.Column(db.String(32))
    surname = db.Column(db.String(64))
    dob = db.Column(db.Date, nullable=False)
    passwordHash = db.Column(db.String(128), index=True)
    verified = db.Column(db.Boolean, nullable=False, default=False)
    passwordSet = db.Column(db.Boolean, nullable=False, default=False)

    def setPassword(self, password):
        self.passwordHash = generate_password_hash(password)
    
    def checkPassword(self, password):
        return check_password_hash(self.passwordHash,password)

    def get_id(self):
        return self.id
    
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')
    
    @staticmethod
    #reset password key contained in email that is hashed for the id
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            print("\n failure")
            return
        return DoctorUser.query.get(id)

class AudioTranscript(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dateCreated = db.Column(db.DateTime, nullable=False)
    dateModified = db.Column(db.DateTime, nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor_user.id'), nullable=False)
    patient_id = db.Column(db.Integer)
    patient_name = db.Column(db.String(128))
    symptoms = db.Column(db.String(1024))
    diagnosis = db.Column(db.String(1024))
    prescription = db.Column(db.String(1024))
    dosage = db.Column(db.String(1024))
    notes = db.Column(db.String(4096))