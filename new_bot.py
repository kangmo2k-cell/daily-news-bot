import os
import smtplib
import ssl
import feedparser
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from urllib.parse import quote

# 뉴스 수집 함수
def fetch_news(keyword):
    encoded_query = quote(keyword)
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"
    try:
        feed = feedparser.parse(rss_url)
        articles = []
        for e in feed.entries[:7]:
            title = e.title.rsplit(" - ", 1)[0]
            source = e.title.rsplit(" - ", 1)[1] if " - " in e.title else "뉴스"
            articles.append({"title": title, "link": e.link, "source": source})
        return articles
    except:
        return []

# 메일 발송 로직
def main():
    user = os.getenv("SMTP_USER")
    pw = os.getenv("SMTP_PASS")
    
    if not user or not pw:
        print("Error: SMTP_USER or SMTP_PASS is missing.")
        return

    keywords = ["중국 전기차 국내 진출", "HBF 반도체", "전고체 배터리"]
    today = datetime.now().strftime("%Y년 %m월 %d일")
    
    html = f'<div style="background-color: #020617; color: #f8fafc; padding: 30px;">'
    html += f'<h1 style="color: #10b981;">KM TECH REPORT ({today})</h1>'
    
    for kw in keywords:
        articles = fetch_news(kw)
        html += f'<h3 style="color: #10b981;">{kw}</h3>'
        for a in articles:
            html += f'<p><a href="{a["link"]}" style="color: #f1f5f9;">· {a["title"]}</a> ({a["source"]})</p>'
    html += '</div>'

    msg = MIMEMultipart()
    msg["Subject"] = f"[{datetime.now().strftime('%m/%d')}] 뉴스 리포트"
    msg["From"] = user
    msg["To"] = user
    msg.attach(MIMEText(html, "html"))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(user, pw)
        server.sendmail(user, user, msg.as_string())
    print("Email sent successfully!")

if __name__ == "__main__":
    main()
