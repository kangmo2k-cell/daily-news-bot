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
    # 환경 변수에서 이메일 계정 정보 로드
    user = os.getenv("SMTP_USER")
    pw = os.getenv("SMTP_PASS")
    
    if not user or not pw:
        print("Error: SMTP_USER or SMTP_PASS environment variables are not set.")
        return

    # 관심 키워드 카테고리화 (가독성 및 관리 용이성 증대)
    categories = {
        "반도체 & AI (HBM/HBF)": ["삼성전자 주가", "SK하이닉스", "HBM 반도체", "HBF 반도체", "엔비디아 관련주"],
        "에너지 & 원자재": ["원유 현물 유가", "WTI 유가 전망", "강관주", "철강 산업 동향"],
        "차세대 모빌리티": ["중국 전기차 국내 진출", "전고체 배터리 기술", "LFP 배터리"],
        "거시 경제": ["미국 금리", "환율 전망"]
    }

    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    
    # 메일 본문 HTML 스타일링
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: 'Malgun Gothic', sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 700px; margin: 0 auto; border: 1px solid #e0e0e0; padding: 20px; }}
            .header {{ background-color: #1a73e8; color: white; padding: 15px; text-align: center; border-radius: 5px 5px 0 0; }}
            .category-box {{ margin-top: 25px; border-bottom: 2px solid #1a73e8; padding-bottom: 5px; }}
            .category-title {{ font-size: 1.2em; color: #1a73e8; font-weight: bold; }}
            .keyword-tag {{ font-size: 0.9em; color: #666; margin-bottom: 10px; }}
            .article-item {{ margin: 10px 0; padding-left: 10px; border-left: 3px solid #f1f3f4; }}
            .article-link {{ text-decoration: none; color: #202124; font-weight: 500; }}
            .article-link:hover {{ text-decoration: underline; color: #1a73e8; }}
            .no-news {{ color: #999; font-style: italic; font-size: 0.9em; }}
            .footer {{ margin-top: 30px; font-size: 0.8em; color: #888; text-align: center; border-top: 1px solid #eee; padding-top: 10px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1 style="margin:0;">KM TECH DAILY REPORT</h1>
                <p style="margin:5px 0 0 0;">{today_str} 업데이트</p>
            </div>
    """

    for cat_name, keywords in categories.items():
        html += f'<div class="category-box"><span class="category-title">{cat_name}</span></div>'
        
        found_any_in_cat = False
        
        for kw in keywords:
            encoded = quote(kw)
            rss = f"https://news.google.com/rss/search?q={encoded}&hl=ko&gl=KR&ceid=KR:ko"
            feed = feedparser.parse(rss)
            
            # 검색 키워드 표시
            current_kw_articles = []
            
            for e in feed.entries[:8]: # 검색 결과 상위 8개 분석
                try:
                    # 발행 시간 확인 (최근 24시간 이내)
                    published_time = datetime(*(e.published_parsed[:6]))
                    if now - published_time < timedelta(hours=24):
                        title = e.title.rsplit(" - ", 1)[0]
                        link = e.link
                        current_kw_articles.append((title, link))
                except Exception:
                    continue
            
            if current_kw_articles:
                found_any_in_cat = True
                html += f'<div class="keyword-tag"># {kw}</div>'
                for title, link in current_kw_articles:
                    html += f'<div class="article-item"><a href="{link}" class="article-link">· {title}</a></div>'
        
        if not found_any_in_cat:
            html += "<p class='no-news'>최근 24시간 내 해당 카테고리의 새로운 이슈가 없습니다.</p>"

    html += f"""
            <div class="footer">
                본 메일은 지정된 키워드를 바탕으로 자동 생성된 리포트입니다.<br>
                © 2024 KM Tech Report Automation
            </div>
        </div>
    </body>
    </html>
    """

    # 이메일 메시지 구성
    msg = MIMEMultipart()
    msg["Subject"] = f"[{today_str}] KM님, 주요 기술 및 시장 뉴스 요약"
    msg["From"] = user
    msg["To"] = user
    msg.attach(MIMEText(html, "html"))

    # 발송 실행
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(user, pw)
            server.sendmail(user, user, msg.as_string())
        print(f"Successfully sent news report for {today_str}")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    main()
