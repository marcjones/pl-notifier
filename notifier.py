import argparse
import os
import re
import requests
import smtplib
import time
from datetime import datetime
from dotenv import load_dotenv
from email.mime.text import MIMEText

# Email Configuration
load_dotenv()
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

# URL and headers for the request
url = "https://footballapi.pulselive.com/content/PremierLeague/text/EN/?sort=timestamp%20desc&limit=1&offset=0&tagNames=fixtures&fullObjectResponse=false"
headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-GB,en;q=0.9",
    "Connection": "keep-alive",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Host": "footballapi.pulselive.com",
    "Origin": "https://www.premierleague.com",
    "Referer": "https://www.premierleague.com/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15"
}

last_seen_id = None
max_retries = 10


def parse_args():
    parser = argparse.ArgumentParser(
        description='Poll the Premier League website for new fixture news.')

    parser.add_argument('-e', '--send-email',
                        help='Send email notifications (Gmail only, must '
                             'provide email address and password in .env).',
                        required=False,
                        action='store_true')

    parser.add_argument('-p', '--polling-interval',
                        help='Interval in minutes between polls. Defaults to '
                             '30 minutes.',
                        type=int, required=False, default=30)

    return parser.parse_args()


def fetch_content_id():
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        # Get the first item in "content"
        if 'content' in data and len(data['content']) > 0:
            latest = data['content'][0]
            return latest['id'], latest['title']
    except Exception as e:
        log(f'Error fetching data')
    return None, None


def send_desktop_notification(message):
    clean_message = clean_text(message)
    title_text = f'with title "Premier League Notifier"'
    soundname_text = f'sound name "default"'
    notification_text = f'display notification "{clean_message}" {title_text} {soundname_text}'
    os.system(f"osascript -e '{notification_text}'")
    log('Notification sent!')


def send_email_notification(message):
    msg = MIMEText(clean_text(message))
    msg['Subject'] = 'PL Notifier - New Fixture News'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_ADDRESS

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, msg.as_string())
            log(f'Email sent!')
    except Exception as e:
        log(f'Error sending email: {e}')


def clean_text(text):
    return re.sub(r'[\\\\\\\'/*?:"<>|]', '', text)


def log(message):
    print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] {message}')


def monitor_new_content(interval: int, email: bool):
    global last_seen_id
    retry_count = 0
    while True:
        log('Checking for new fixture news...')
        latest_id, latest_title = fetch_content_id()
        if latest_id is None:
            if retry_count < max_retries:
                log('Failed to fetch data. Retrying...')
                retry_count += 1
                time.sleep(5)
            else:
                log(f'Failed to fetch data after {max_retries} attempts')
                time.sleep(interval)
        else:
            if last_seen_id is None:
                # If this is the first time we're running, store the latest ID
                log('Started watching for fixture news')
                send_desktop_notification(
                    f'Started watching for fixture news')
                last_seen_id = latest_id
            elif latest_id != last_seen_id:
                # If we haven't seen this ID before, send notifications and
                # update the last seen ID
                log(f'New fixture news found: {latest_title}')
                send_desktop_notification(latest_title)
                if email:
                    send_email_notification(latest_title)
                last_seen_id = latest_id
            else:
                log('No new fixture news found')

            time.sleep(interval)


if __name__ == "__main__":
    args = parse_args()
    monitor_new_content(args.polling_interval * 60, args.send_email)
