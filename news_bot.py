import os
import smtplib
import ssl
import feedparser
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from urllib.parse import quote

def main():
    user = os.getenv("SMTP_USER")
    pw = os.getenv("SMTP_PASS")
    
    if not user or not pw:
        print("Error: Secrets not found")
        return

    keywords = ["중국 전기차 국내 진출", "HBF 반도체", "전고체 배터리"]
    today = datetime.now().strftime("%Y-%m-%d")
    
    html = f"<h1>KM TECH REPORT ({today})</h1>"
    for kw in keywords:
        encoded = quote(kw)
        rss = f"https://news.google.com/rss/search?q={encoded}&hl=ko&gl=KR&ceid=KR:ko"
        feed = feedparser.parse(rss)
        html += f"<h3>{kw}</h3>"
        for e in feed.entries[:7]:
            title = e.title.rsplit(" - ", 1)[0]
            html += f'<p><a href="{e.link}">{title}</a></p>'

    msg = MIMEMultipart()
    msg["Subject"] = f"[{today}] 뉴스 리포트"
    msg["From"] = user
    msg["To"] = user
    msg.attach(MIMEText(html, "html"))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(user, pw)
        server.sendmail(user, user, msg.as_string())
    print("Done!")

if __name__ == "__main__":
    main()
