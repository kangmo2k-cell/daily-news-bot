import os
import smtplib
import ssl
import feedparser
import time
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from urllib.parse import quote

def main():
    user = os.getenv("SMTP_USER")
    pw = os.getenv("SMTP_PASS")
    if not user or not pw: return

    keywords = ["중국 전기차 국내 진출", "HBF 반도체", "전고체 배터리"]
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    
    html = f"<h1>KM TECH REPORT ({today_str})</h1>"
    
    for kw in keywords:
        encoded = quote(kw)
        rss = f"https://news.google.com/rss/search?q={encoded}&hl=ko&gl=KR&ceid=KR:ko"
        feed = feedparser.parse(rss)
        
        html += f"<h3>{kw}</h3>"
        found_new_article = False
        
        for e in feed.entries[:10]:
            # 발행 시간 확인 (최근 24시간 이내인지 체크)
            published_time = datetime(*(e.published_parsed[:6]))
            if now - published_time < timedelta(hours=24):
                title = e.title.rsplit(" - ", 1)[0]
                html += f'<p><a href="{e.link}">· {title}</a></p>'
                found_new_article = True
        
        if not found_new_article:
            html += "<p style='color:gray;'>최근 24시간 내 새로운 기사가 없습니다.</p>"

    msg = MIMEMultipart()
    msg["Subject"] = f"[{today_str}] KM님, 오늘의 뉴스 요약입니다"
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
