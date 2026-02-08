import os
import requests
import json
from datetime import datetime
import re
import sys
import xml.etree.ElementTree as ET

# --- KONFIGURASI ---
ADSTERRA_SOCIAL_BAR = """<script src="https://pl28671543.effectivegatecpm.com/b4/04/60/b40460008fe491a20d7ed511234ef60c.js"></script>"""
ADSTERRA_DIRECT_LINK = "https://www.effectivegatecpm.com/scpufanss?key=91a5369ee9e711e8e1f77e2491d62f65"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("ERROR: API Key tidak ditemukan!")
    sys.exit(1)

def get_trending_news():
    print("1. Mengambil berita terbaru dari RSS...")
    rss_url = "https://news.google.com/rss/search?q=finance+technology+usa&hl=en-US&gl=US&ceid=US:en"
    response = requests.get(rss_url)
    root = ET.fromstring(response.content)
    item = root.find('.//item')
    return item.find('title').text

def generate_article_manual(news_title):
    print(f"2. Menyusun artikel via API HTTP Manual: {news_title}")
    
    # URL API Resmi Google (Gunakan v1 agar lebih stabil, bukan v1beta)
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    prompt = f"Write a 500-word blog post in English about: '{news_title}'. Format: [TITLE] title [DESC] desc [CONTENT] html content [IMG] image prompt"
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    if response.status_code != 200:
        print(f"API Error: {response.text}")
        sys.exit(1)
        
    res_json = response.json()
    return res_json['candidates'][0]['content']['parts'][0]['text']

def main():
    try:
        news_title = get_trending_news()
        raw_text = generate_article_manual(news_title)
        
        # Ekstraksi Data
        title = re.search(r"\[TITLE\](.*)", raw_text, re.IGNORECASE).group(1).strip()
        desc = re.search(r"\[DESC\](.*)", raw_text, re.IGNORECASE).group(1).strip()
        content = re.search(r"\[CONTENT\](.*)\[IMG\]", raw_text, re.IGNORECASE | re.DOTALL).group(1).strip()
        img_p = re.search(r"\[IMG\](.*)", raw_text, re.IGNORECASE).group(1).strip()

        img_url = f"https://pollinations.ai/p/{img_p.replace(' ', '%20')}?width=800&height=600&seed={datetime.now().second}"

        if not os.path.exists("posts"): os.makedirs("posts")
        filename = re.sub(r'[^a-zA-Z0-9]', '-', title.lower()).strip('-') + ".html"
        filepath = f"posts/{filename}"
        
        html_post = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>{title}</title><link rel="stylesheet" href="../style.css">{ADSTERRA_SOCIAL_BAR}</head><body><nav><a href="../index.html">← Home</a></nav><article><h1>{title}</h1><img src="{img_url}" style="width:100%;border-radius:10px;"><div class='article-content'>{content}</div><br><center><a href='{ADSTERRA_DIRECT_LINK}' class='cta-button'>Read More</a></center></article></body></html>"""
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_post)

        with open("index.html", "r", encoding="utf-8") as f:
            index_content = f.read()
        
        new_link = f'<li><a href="{filepath}">{title}</a> - <small>{datetime.now().strftime("%Y-%m-%d")}</small></li>\n'
        marker = '<!-- Script Bot akan otomatis menambah daftar artikel di sini -->'
        
        if marker in index_content:
            new_index = index_content.replace(marker, marker + "\n" + new_link)
            with open("index.html", "w", encoding="utf-8") as f:
                f.write(new_index)

        print(f"BERHASIL TOTAL: Artikel '{title}' terbit!")

    except Exception as e:
        print(f"FAILED: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
