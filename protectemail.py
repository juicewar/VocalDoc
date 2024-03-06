def protectEmail(email):
    return email[0:2] + "***" + email[email.find("@")-2:]