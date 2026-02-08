import os
import requests
import json
from datetime import datetime
import re
import sys
import xml.etree.ElementTree as ET
import random

# --- KONFIGURASI ---
ADSTERRA_SOCIAL_BAR = """<script src="https://pl28671543.effectivegatecpm.com/b4/04/60/b40460008fe491a20d7ed511234ef60c.js"></script>"""
ADSTERRA_DIRECT_LINK = "https://www.effectivegatecpm.com/scpufanss?key=91a5369ee9e711e8e1f77e2491d62f65"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# URL DASAR ANDA (Ganti dengan milik Anda)
GITHUB_BASE_URL = "https://bertoantonio9695-dev.github.io/optimator-news-hub"
VERCEL_BASE_URL = "https://optimator-news-hub.vercel.app" # Ganti jika beda

def get_trending_news():
    print("1. Mengambil berita...")
    rss_url = "https://news.google.com/rss/search?q=finance+technology+usa&hl=en-US&gl=US&ceid=US:en"
    response = requests.get(rss_url, timeout=15)
    root = ET.fromstring(response.content)
    items = root.findall('.//item')
    selected_item = random.choice(items[:10]) 
    return selected_item.find('title').text

def generate_article_groq(news_title):
    print("2. Menyusun artikel...")
    url = "https://api.groq.com/openai/v1/chat/completions"
    prompt = f"Write a 500-word blog post in English about: '{news_title}'. Format: [TITLE] title [DESC] short description [CONTENT] html content [IMG] short image prompt"
    payload = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}]}
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    return response.json()['choices'][0]['message']['content']

def update_rss(title, filename, img_url, desc):
    print("3. Memperbarui RSS Feed...")
    rss_file = "rss.xml"
    
    # PILIH URL SECARA ACAK (GitHub atau Vercel)
    chosen_base = random.choice([GITHUB_BASE_URL, VERCEL_BASE_URL])
    post_link = f"{chosen_base}/posts/{filename}"
    
    new_item = f"""
    <item>
        <title>{title}</title>
        <link>{post_link}</link>
        <description>{desc}</description>
        <pubDate>{datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')}</pubDate>
        <enclosure url="{img_url}" length="0" type="image/jpeg" />
        <guid>{post_link}</guid>
    </item>"""

    if not os.path.exists(rss_file):
        rss_content = f'<?xml version="1.0" encoding="UTF-8" ?><rss version="2.0"><channel><title>Tier 1 Insights</title><link>{GITHUB_BASE_URL}</link><description>Daily Trends</description>{new_item}</channel></rss>'
    else:
        with open(rss_file, "r", encoding="utf-8") as f:
            rss_content = f.read()
        rss_content = rss_content.replace("</channel>", f"{new_item}</channel>")

    with open(rss_file, "w", encoding="utf-8") as f:
        f.write(rss_content)

def main():
    if not GROQ_API_KEY: sys.exit(1)
    try:
        news_title = get_trending_news()
        clean_news_title = news_title.split(" - ")[0].strip()
        
        if os.path.exists("index.html"):
            with open("index.html", "r", encoding="utf-8") as f:
                if clean_news_title in f.read(): return 

        raw_text = generate_article_groq(news_title)
        title = re.search(r"\[TITLE\](.*)", raw_text, re.I).group(1).strip()
        desc = re.search(r"\[DESC\](.*)", raw_text, re.I).group(1).strip()
        content = re.search(r"\[CONTENT\](.*)\[IMG\]", raw_text, re.I|re.S).group(1).strip()
        img_p = re.search(r"\[IMG\](.*)", raw_text, re.I).group(1).strip()

        img_url = f"https://image.pollinations.ai/prompt/{img_p.replace(' ', '%20')}?width=800&height=600&nologo=true&seed={random.randint(1,999)}"

        if not os.path.exists("posts"): os.makedirs("posts")
        filename = re.sub(r'[^a-zA-Z0-9]', '-', title.lower()).strip('-') + ".html"
        
        with open(f"posts/{filename}", "w", encoding="utf-8") as f:
            f.write(f"<html><head><title>{title}</title><link rel='stylesheet' href='../style.css'>{ADSTERRA_SOCIAL_BAR}</head><body><article><h1>{title}</h1><img src='{img_url}' style='width:100%'><div class='content'>{content}</div><center><a href='{ADSTERRA_DIRECT_LINK}' class='cta-button'>READ MORE</a></center></article></body></html>")

        # UPDATE RSS DAN INDEX
        update_rss(title, filename, img_url, desc)
        
        with open("index.html", "r", encoding="utf-8") as f:
            index_content = f.read()
        new_link = f'<li><a href="posts/{filename}">{title}</a></li>\n'
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(index_content.replace("<!-- Script Bot akan otomatis menambah daftar artikel di sini -->", f"<!-- Script Bot akan otomatis menambah daftar artikel di sini -->\n{new_link}"))

        print(f"BERHASIL: {title}")
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    main()
