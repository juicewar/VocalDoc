from flask_mail import Message
from app import mail, app
from flask import render_template
from threading import Thread

#asynchronous processing
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)  

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    #sends email asynchronously as not to slow processing of the program
    Thread(target=send_async_email, args=(app, msg)).start()
    print("email sent")

def sendPasswordResetEmail(user):
    token = user.get_reset_password_token()
    send_email('[VocalDoc] Reset Your Password',
               sender=app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password_email.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password_email.html',
                                         user=user, token=token))

def protectEmail(email):
    return email[0:2] + "***" + email[email.find("@")-2:]