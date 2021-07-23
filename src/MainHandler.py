import json
import os
import shutil
import sys
import time

sys.path.insert(0, '../src')

from EmailHandler import EmailHandler
from DownloadHandler import DownloadHandler

EMAIL_MAX_SIZE = 25     # maximum send size in MegaBytes
MAX_VIDEO_LENGTH = 10   # maximum length of videos to download in minutes
MAX_RETRY = 10          # maximum number of times to retry on error


class MainHandler(object):

    def __init__(self, secrets_: dict, email_handler_: EmailHandler, download_handler_: DownloadHandler):
        self.secrets = secrets_
        self.email_handler = email_handler_
        self.download_handler = download_handler_

    def start(self, retry):
        while True:
            try:
                emails = self.email_handler.get_all_emails()
            except Exception as e:
                self.email_handler.send_error('Error while getting emails.', e)
                # for HTTPError 403: try |youtube-dl --rm-cache-dir|
            else:
                if len(emails) > 0:
                    print('you\'ve got mail')
                    # loop over all Emails, there may be plenty
                    for email in emails:
                        try:
                            folder_name = self.download_handler.download_videos(email.youtube_links)
                        except Exception as e:
                            self.email_handler.send_error('Error while downloading youtube video, Restarting.', e)
                            if retry < MAX_RETRY:
                                self.start(retry + 1)
                        else:
                            try:
                                # send answer, attach all mails in folder folder_name
                                self.email_handler.send_response(email, folder_name)
                            except Exception as e:
                                self.email_handler.send_error('Error while sending response emails.', e, email, folder_name)
                                if retry < MAX_RETRY:
                                    self.start(retry + 1)
                                break
                            else:
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
    email_handler = EmailHandler(secrets, EMAIL_MAX_SIZE)

    # initialize DownloadHandler
    download_handler = DownloadHandler(path, MAX_VIDEO_LENGTH)

    # start
    main_handler = MainHandler(secrets, email_handler, download_handler)
    main_handler.start(0)


if __name__ == "__main__":
    main()
