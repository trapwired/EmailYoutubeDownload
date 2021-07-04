import json
import os
import shutil
import time

from EmailHandler import EmailHandler
from src.DownloadHandler import DownloadHandler


class MainHandler(object):

    def __init__(self, secrets_: dict, email_handler_: EmailHandler, download_handler_: DownloadHandler):
        self.secrets = secrets_
        self.email_handler = email_handler_
        self.download_handler = download_handler_

    def start(self):
        while True:
            emails = self.email_handler.get_all_emails()
            if len(emails) > 0:
                print('you\'ve got mail')
                # loop over all Emails, there may be plenty
                for email in emails:
                    folder_name = self.download_handler.download_videos(email.youtube_links)
                    # send answer, attach all mails in folder folder_name
                    self.email_handler.send_response(email, folder_name)
                    # delete folder
                    shutil.rmtree(folder_name)
                    # delete email from Inbox / move to folder
                    self.email_handler.delete_successful(email)
                self.email_handler.imap_connection.expunge()
            time.sleep(10)


def get_secrets(path):
    with open(path) as f:
        return json.load(f)


def main():
    # root path
    path = '/'.join((os.path.abspath(__file__).replace('\\', '/')).split('/')[:-2])
    secrets = get_secrets(os.path.join(path, "secrets.json"))

    # initialize email_handler
    email_handler = EmailHandler(secrets)

    # initialize DownloadHandler
    download_handler = DownloadHandler(path)

    # start
    main_handler = MainHandler(secrets, email_handler, download_handler)
    main_handler.start()


if __name__ == "__main__":
    main()
