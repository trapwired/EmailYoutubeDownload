# Youtube download via email
This simple script downloads and replies to an email containing youtube links.

## Setup
- Install the requirements via the provided requirements.txt file (easiest to do via venv)
- Install youtube-dl for python and ffmpeg files as provided via [this Link](https://github.com/ytdl-org/youtube-dl)
- create a secrets.json file and place in it the root directory
- get a gmail api-key from google

## Usage
Entry point is MainHandler.py - the script runs an while True loop:
- download mails from your Inbox
- looks whether the senders are in the allowed_senders list
- if so, checks the emails for youtube links
- if there are any, download them all into a new temporary folder inside downloads/
- reply to the original email with the same subject and the downloaded mp3's attached
- delete the original email from your Inbox
- wait for 10 seconds

## secrets.json
```python
{
  "username_email" : "some_email@gmail.com",
  "password_email" : "API_KEY",
  "allowed_senders" : [
    "some_email@hotmail.com",
    "another_email@aol.com"
  ]
}
```
