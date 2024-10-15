# pl-notifier
A Python script for MacOS that polls the Premier League website for fixture news articles and notifies by desktop notification and (optionally) email when new articles are posted.

## Setup
- Clone the repo
- Install dependencies: `pip install -r requirements.txt`
- Optional for receiving email notifications - make a copy of `.env.template` named `.env` and add your Gmail email address and password (DO NOT use your Gmail login password, you will need to generate an [app password](https://support.google.com/mail/answer/185833?hl=en-GB)) 

## Running
### Default settings
Run the script with default settings (desktop notifications only and polling every 30 minutes):

`python3 notifier.py`

### Optional arguments
- `-e` or `--send-email` to enable email notifications (Gmail credentials must be provided in `.env`)
- `-p` or `--polling-interval` to adjust the interval between polling  (default is 30 minutes)

Example, to enable email notifications and set the polling interval to once every 60 minutes:

`python3 notifier.py -e -p 60`

### Stop
`Ctrl+C` to stop the script.
