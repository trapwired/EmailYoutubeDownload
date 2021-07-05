# Youtube download via email
This simple script downloads and replies with the mp3's to an email containing youtube links.

## Setup
- Install the requirements via the provided requirements.txt file 
- create a secrets.json file and place in it the root directory
- create a downloads folder in the root directory (where the temporary files are stored)
- if you do not use 2FA to login into your google account, your normal credentials can be used (Username and password). If 2FA is used, you need to generate an app-password ([Creating App Passwords](https://support.google.com/mail/answer/185833?hl=en))

If there are any youtube-dl or ffmpeg related errors, consider looking at their [Github-Page](https://github.com/ytdl-org/youtube-dl)

## Usage
Entry point is MainHandler.py - the script runs an while True loop:
- download mails from your Inbox
- looks whether the senders are in the allowed_senders list
- if so, checks the emails for youtube links (multiple allowed)
- if there are any, download them all into a new temporary folder inside downloads/
- reply to the original email with the same subject and the downloaded mp3's attached
- delete the original email from your Inbox
- wait for 10 seconds

If there is any error, an email containing said error will be sent to 'error_email' specified in secrets.json

## secrets.json
```python
{
  "username_email" : "some_email@gmail.com",
  "password_email" : "app_pasword OR normal_password",
  "error_email" : "admin_email@gmail.com",
  "allowed_senders" : [
    "some_email@hotmail.com",
    "another_email@outlook.com",
    "a_third_email@icloud.com"
  ]
}
```
# Limitations
- there is no advanced error catching
- there is no advanced logging
- there is no check for send-limits: if the downloaded video is larger than the eMail-providers send-limit, an error will be thrown - same if several mp3 are downloaded and they sum up together to more than the send-limit
