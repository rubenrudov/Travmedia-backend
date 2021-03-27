"""
Author: Ruben Rudov
Purpose: Class for handling mail sending from the server to a new user that was inserted to the database
"""

import smtplib, ssl


class MailHandler:
    def __init__(self, email_to, username):
        self.email_from = "ruby.rudov@gmail.com"    # TODO: Open an E-mail for Travmedia and change mine to it
        self.__password = "qmjleavwpadzajkr"        # TODO: Add an app-password for Travmedia
        self.email_to = email_to
        self.username = username

    def send_email(self):
        port = 587
        smtp_server = "smtp.gmail.com"
        message = f"""\
        Subject: Hey {self.username}

        Hey {self.username}, welcome to Travmedia, the new home for travelers"""

        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_server, port) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(self.email_from, self.__password)
            server.sendmail(self.email_from, self.email_to, message)
            print(f"Sent mail to {self.email_to} from {self.email_from}")

    def __str__(self):
        print(f"Mail handler that sends email from {self.email_from} to {self.email_to} via a SMTP socket")


