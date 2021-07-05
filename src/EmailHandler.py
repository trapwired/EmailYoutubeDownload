import email
import imaplib
import math
import os
import smtplib
import re
from email import encoders
from email.header import decode_header
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from bs4 import BeautifulSoup as bs

from src.EMail import YoutubeEmail


def split_html(string, maxsplit=0):
    delimiters = " ", "\"", "<", ">"
    regexPattern = '|'.join(map(re.escape, delimiters))
    return re.split(regexPattern, string, maxsplit)


def get_links(email_body, isHTML=False):
    if isHTML:
        split = split_html(email_body)
    else:
        split = email_body.splitlines()
    res = []
    for line in split:
        if 'youtu' in line:
            split = line.split(' ')
            for word in split:
                if word.startswith('http'):
                    res.append(word)
    return res


def get_filename(file):
    res = file.replace(' ', '_')
    res = res.replace('ä', 'ae')
    res = res.replace('ö', 'oe')
    res = res.replace('ü', 'ue')
    return res


class EmailHandler(object):
    def __init__(self, secrets_: dict, max_size_: int):
        self.secrets = secrets_
        self.max_size = max_size_
        self.imap_connection = self.init_imap_connection()

    def init_imap_connection(self):
        # create an IMAP4 class with SSL
        imap = imaplib.IMAP4_SSL("imap.gmail.com")
        # authenticate
        imap.login(self.secrets['username_email'], self.secrets['password_email'])
        return imap

    def get_all_emails(self):
        status, messages = self.imap_connection.select("INBOX")
        messages = int(messages[0])
        result = []
        for i in range(1, messages + 1):
            # fetch the email message by ID
            res, msg = self.imap_connection.fetch(str(i), "(RFC822)")
            for response in msg:
                if isinstance(response, tuple):
                    # parse a bytes email into a message object
                    msg = email.message_from_bytes(response[1])
                    # decode the email subject
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        # if it's a bytes, decode to str
                        subject = subject.decode(encoding)
                    # decode email sender
                    sender, encoding = decode_header(msg.get("From"))[0]
                    if isinstance(sender, bytes):
                        sender = sender.decode(encoding)
                    sender = sender.split('<')[1]
                    sender = sender.split('>')[0]
                    if sender not in self.secrets['allowed_senders']:
                        # Do nothing if not from specific sender
                        continue

                    # extract content type of email
                    content_type = msg.get_content_type()
                    if msg.is_multipart():
                        body = ' '
                        links = []
                        for part in msg.get_payload():
                            if part.get_content_type() == "text/plain":
                                body += part.get_payload(decode=True).decode()
                                links = links + get_links(str(body))
                            if part.get_content_type() == "text/html":
                                body += part.get_payload(decode=True).decode()
                                links = links + get_links(str(body), True)
                    else:
                        body = msg.get_payload(decode=True).decode()
                        if content_type == "text/plain":
                            links = get_links(str(body))
                        elif content_type == "text/html":
                            links = get_links(str(body), True)
                        else:
                            raise Exception(f'unknown email body type: {content_type}')
                    # remove duplicates from links
                    links_wo_duplicates = list(dict.fromkeys(links))
                    result.append(YoutubeEmail(sender, subject, links_wo_duplicates, i))
        return result

    def send_response(self, mail: YoutubeEmail, folder):
        onlyfiles = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]

        # initialize the SMTP server
        server = smtplib.SMTP("smtp.gmail.com", 587)
        # connect to the SMTP server as TLS mode (secure) and send EHLO
        server.starttls()
        # login to the account using the credentials
        server.login(self.secrets['username_email'], self.secrets['password_email'])

        index = 1
        for file in onlyfiles:
            count_part = ' (' + str(index) + '/' + str(len(onlyfiles)) + ')'
            index += 1
            msg = MIMEMultipart()
            msg["Subject"] = 'Re: ' + mail.subject + count_part
            msg["From"] = self.secrets['username_email']
            msg["To"] = mail.from_email

            html = "Folgendes Video heruntergeladen:\n\n\t" + file

            # make the text version of the HTML
            text = bs(html, "html.parser").text
            text_part = MIMEText(text, "plain")

            filename = os.path.join(folder, file)
            # Open file in binary mode
            size = round(os.path.getsize(filename) / math.pow(2, 20), 2)
            # print('Size of file is', size, 'MB')
            if size > self.max_size - 1:
                html = "Folgendes Video konnte nicht heruntergeladen werden:\n\n\t" + file + "\n\nGrund: Zu gross, " \
                                                                                             "um via eMail zu " \
                                                                                             "senden... "
                text = bs(html, "html.parser").text
                text_part = MIMEText(text, "plain")
                msg.attach(text_part)
            else:
                msg.attach(text_part)
                with open(filename, "rb") as attachment:
                    # Add file as application/octet-stream
                    # Email client can usually download this automatically as attachment
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())
                # Encode file in ASCII characters to send by email
                encoders.encode_base64(part)
                # Add header as key/value pair to attachment part
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={get_filename(file)}",
                )
                msg.attach(part)
            # send the email
            server.sendmail(self.secrets['username_email'], mail.from_email, msg.as_string())
            print(f'sent email to {mail.from_email} {count_part}')
        # terminate the SMTP session
        server.quit()

    def delete_successful(self, mail: YoutubeEmail):
        self.imap_connection.store(str(mail.msg_index), "+FLAGS", "\\Deleted")

    def send_error(self, error):
        msg = MIMEMultipart()
        msg["Subject"] = 'Error occured'
        msg["From"] = self.secrets['username_email']
        msg["To"] = self.secrets['error_email']

        html = "Error occured: " + str(error)

        # make the text version of the HTML
        text = bs(html, "html.parser").text
        text_part = MIMEText(text, "plain")
        # html_part = MIMEText(html, "html")
        # attach the email body to the mail message
        # attach the plain text version first
        msg.attach(text_part)
        # msg.attach(html_part)

        # initialize the SMTP server
        server = smtplib.SMTP("smtp.gmail.com", 587)
        # connect to the SMTP server as TLS mode (secure) and send EHLO
        server.starttls()
        # login to the account using the credentials
        server.login(self.secrets['username_email'], self.secrets['password_email'])
        # send the email
        server.sendmail(self.secrets['username_email'], self.secrets['error_email'], msg.as_string())
        # terminate the SMTP session
        server.quit()


