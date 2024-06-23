import requests
import smtplib
from email.mime.text import MIMEText
import time
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

GITHUB_API_URL = "https://api.github.com"
REPOS = [
]
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = "pcfbgjqmjmigfnrk"  
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")

logging.info(f"Loaded SENDER_EMAIL: {SENDER_EMAIL}")
logging.info(f"Loaded RECIPIENT_EMAIL: {RECIPIENT_EMAIL}")

def get_latest_issue(repo):
    """Fetch the latest issue from a GitHub repository."""
    url = f"{GITHUB_API_URL}/repos/{repo}/issues"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers)
    issues = response.json()
    if issues:
        logging.info(f"Latest issue for {repo}: {issues[0]['title']} (#{issues[0]['number']})")
    else:
        logging.info(f"No issues found for {repo}.")
    return issues[0] if issues else None

def send_email(subject, body):
    """Send an email notification."""
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
    logging.info(f"Email sent: {subject}")

def check_new_issues():
    """Check for new issues in the specified GitHub repositories and send email notifications."""
    for repo in REPOS:
        latest_issue = get_latest_issue(repo)
        if latest_issue:
            issue_number = latest_issue['number']
            issue_title = latest_issue['title']
            issue_url = latest_issue['html_url']

            issue_file = f"{repo.replace('/', '_')}_latest_issue.txt"
            
            if not os.path.exists(issue_file):
                with open(issue_file, "w") as f:
                    f.write(str(issue_number))
                continue

            with open(issue_file, "r") as f:
                last_seen_issue = int(f.read().strip())

            if issue_number > last_seen_issue:
                subject = f"New Issue in {repo}"
                body = f"New issue raised in {repo}:\n\nTitle: {issue_title}\nURL: {issue_url}"
                send_email(subject, body)

                with open(issue_file, "w") as f:
                    f.write(str(issue_number))
            else:
                logging.info(f"No new issues for {repo}.")

def main():
    """Main loop to check for new issues periodically."""
    while True:
        logging.info("Checking for new issues...")
        check_new_issues()
        time.sleep(60) 

if __name__ == "__main__":
    main()
