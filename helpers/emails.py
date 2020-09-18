import yagmail

class Sender(object):
    def __init__(self, sender_email, password):
        self.sender_email = sender_email
        self.password = password
    # def sendEmail(self, email):

class Email():
    def __init__(self, *args, **kwargs):
        if kwargs.get('message', None) == None:
            self.message = kwargs.get('msg', None)
        else:
            self.message = kwargs.get('message', None)
        self.subject = kwargs.get('subject', None)
        self.to = kwargs.get('to', None)

if __name__ == "__main__":
    password = input("password: ")
    sender = Sender("999pigcake@gmail.com", password)
    email = Email(msg="test", to="999pigcake@gmail.com", subject="testtttttttttttt")
    yag = yagmail.SMTP(sender.sender_email, sender.password)
    yag.send(
        to=email.to,
        subject=email.subject,
        contents=email.message
    )
    yag.close()