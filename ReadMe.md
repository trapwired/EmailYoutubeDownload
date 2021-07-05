# Youtube download via email

This simple script downloads and replies with the mp3's to an email containing youtube links.

## Setup

- install the requirements via the provided requirements.txt file
- create a secrets.json file and place in it the root directory
- create a downloads folder in the root directory (where the temporary files are stored)
- if you do not use 2FA to login into your google account, your normal credentials can be used (Username and password).
  If 2FA is used, you need to generate an
  app-password ([Creating App Passwords](https://support.google.com/mail/answer/185833?hl=en))

If there are any youtube-dl or ffmpeg related errors, consider looking at
their [Github-Page](https://github.com/ytdl-org/youtube-dl).

## Usage

Entry point is MainHandler.py - the script runs an while True loop:

- download mails from your Inbox
- looks whether the senders are in the allowed_senders list
- if so, checks the emails for youtube links (multiple allowed)
- if there are any, download them all into a new temporary folder inside downloads/
- reply to the original email with the same subject and the downloaded mp3's attached, send one email for each attachement
- delete the original email from your Inbox
- wait for 10 seconds

If there is any error, an email containing said error will be sent to 'error_email' specified in secrets.json
### Global Variables (MainHandler.py)
```python
EMAIL_MAX_SIZE = 25                         # maximum send size, in MegaBytes
MAX_VIDEO_LENGTH = 10                       # maximum length of videos to download, in Minutes
```
## secrets.json

```python
{
    "username_email": "some_email@gmail.com",
    "password_email": "app_pasword OR normal_password",
    "error_email": "admin_email@gmail.com",
    "allowed_senders": [
        "some_email@hotmail.com",
        "another_email@outlook.com",
        "a_third_email@icloud.com"
    ]
}
```

# Limitations

- there is no advanced error catching (just one big try - except clause around the main loop)
- there is no advanced logging (letting it run headless on a pi is not easy to debug)
- send-limit: if the downloaded mp3 is larger than gmails send limit (25MB), it cant be sent back (but still sends a
  message to the original sender stating the reason)
