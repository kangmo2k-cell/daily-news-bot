import os
import smtplib
import ssl
import feedparser
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from urllib.parse import quote

class NewsAutomation:
    def __init__(self, smtp_host, smtp_port, smtp_user, smtp_pass):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.sender_email = smtp_user
        self.sender_password = smtp_pass
        self.receiver_email = smtp_user
        self.keywords = ["중국 전기차 국내 진출", "HBF 반도체", "전고체 배터리"]
        self.items_per_keyword = 7

    def fetch_news(self, keyword):
        encoded_query = quote(keyword)
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"
        try:
            feed = feedparser.parse(rss_url)
            return [{"title": e.title.rsplit(" - ", 1)[0], "link": e.link, "source": e.title.rsplit(" - ", 1)[1] if " - " in e.title else "뉴스"} for e in feed.entries[:self.items_per_keyword]]
        except: return []

    def build_html(self, news_data):
        today = datetime.now().strftime("%Y년 %m월 %d일")
        html = f'<div style="background-color: #020617; color: #f8fafc; padding: 30px;"><h1 style="color: #10b981;">KM TECH REPORT ({today})</h1>'
        for kw, arts in news_data.items():
            html += f'<h3 style="color: #10b981;">{kw}</h3>'
            for a in arts:
                html += f'<p><a href="{a["link"]}" style="color: #f1f5f9;">· {a["title"]}</a> ({a["source"]})</p>'
        return html + "</div>"

    def send_daily_email(self):
        all_news = {kw: self.fetch_news(kw) for kw in self.keywords}
        msg = MIMEMultipart(); msg['Subject'] = f"[{datetime.now().strftime('%m/%d')}] 뉴스 리포트"; msg['From'] = self.sender_email; msg['To'] = self.receiver_email
        msg.attach(MIMEText(self.build_html(all_news), 'html'))
        with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, context=ssl.create_default_context()) as server:
            server.login(self.sender_email, self.sender_password)
            server.sendmail(self.sender_email, self.receiver_email, msg.as_string())

if __name__ == "__main__":
    user = os.getenv('SMTP_USER')
    pw = os.getenv('SMTP_PASS')
    bot = NewsAutomation('smtp.gmail.com', 465, user, pw)
    bot.send_daily_email()
