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
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def get_trending_news():
    print("1. Mengambil berita dari Google News RSS...")
    try:
        rss_url = "https://news.google.com/rss/search?q=finance+technology+usa&hl=en-US&gl=US&ceid=US:en"
        response = requests.get(rss_url, timeout=15)
        root = ET.fromstring(response.content)
        item = root.find('.//item')
        return item.find('title').text
    except Exception as e:
        print(f"Gagal ambil RSS: {e}")
        return "New Financial Technology Trends in USA 2026"

def generate_article_groq(news_title):
    print(f"2. Menyusun artikel via Groq Cloud: {news_title}")
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    prompt = f"Write a 500-word professional blog post in English about: '{news_title}'. Format output strictly as: [TITLE] title [DESC] short description [CONTENT] html content [IMG] short image prompt"
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}]
    }
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    
    if response.status_code != 200:
        print(f"Groq API Error: {response.text}")
        sys.exit(1)
        
    return response.json()['choices'][0]['message']['content']

def main():
    if not GROQ_API_KEY:
        print("ERROR: GROQ_API_KEY tidak ditemukan di Secrets!")
        sys.exit(1)

    try:
        news_title = get_trending_news()
        raw_text = generate_article_groq(news_title)
        
        # Ekstraksi Data
        title = re.search(r"\[TITLE\](.*)", raw_text, re.I).group(1).strip()
        desc = re.search(r"\[DESC\](.*)", raw_text, re.I).group(1).strip()
        content = re.search(r"\[CONTENT\](.*)\[IMG\]", raw_text, re.I|re.S).group(1).strip()
        img_p = re.search(r"\[IMG\](.*)", raw_text, re.I).group(1).strip()

        img_url = f"https://pollinations.ai/p/{img_p.replace(' ', '%20')}?width=800&height=600&seed={datetime.now().second}"

        if not os.path.exists("posts"): os.makedirs("posts")
        filename = re.sub(r'[^a-zA-Z0-9]', '-', title.lower()).strip('-') + ".html"
        filepath = f"posts/{filename}"
        
        html_post = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>{title}</title><link rel="stylesheet" href="../style.css">{ADSTERRA_SOCIAL_BAR}</head><body><nav><a href="../index.html">← Home</a></nav><article><h1>{title}</h1><img src="{img_url}" style="width:100%;border-radius:10px;"><div class='article-content'>{content}</div><br><center><a href='{ADSTERRA_DIRECT_LINK}' class='cta-button'>Read More</a></center></article></body></html>"""
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_post)

        if os.path.exists("index.html"):
            with open("index.html", "r", encoding="utf-8") as f:
                index_content = f.read()
            new_link = f'<li><a href="{filepath}">{title}</a> - <small>{datetime.now().strftime("%Y-%m-%d")}</small></li>\n'
            marker = '<!-- Script Bot akan otomatis menambah daftar artikel di sini -->'
            new_index = index_content.replace(marker, marker + "\n" + new_link) if marker in index_content else index_content.replace("</ul>", new_link + "</ul>")
            with open("index.html", "w", encoding="utf-8") as f:
                f.write(new_index)

        print(f"BERHASIL: {title} terbit via Groq!")

    except Exception as e:
        print(f"FAILED: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
