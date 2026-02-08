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

GITHUB_BASE_URL = "https://bertoantonio9695-dev.github.io/optimator-news-hub"
VERCEL_BASE_URL = "https://optimator-news-hub.vercel.app"

def get_trending_news():
    print("LOG: Mengambil berita dari Google News...")
    rss_url = "https://news.google.com/rss/search?q=finance+technology+usa&hl=en-US&gl=US&ceid=US:en"
    response = requests.get(rss_url, timeout=15)
    root = ET.fromstring(response.content)
    items = root.findall('.//item')
    # Ambil 15 berita teratas agar variasi lebih banyak
    selected_item = random.choice(items[:15]) 
    return selected_item.find('title').text

def generate_article_groq(news_title):
    print(f"LOG: Menyusun artikel via Groq: {news_title}")
    url = "https://api.groq.com/openai/v1/chat/completions"
    prompt = f"Write a 500-word blog post in English about: '{news_title}'. Format output strictly as: [TITLE] title [DESC] short description [CONTENT] html content [IMG] short image prompt"
    payload = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}]}
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    return response.json()['choices'][0]['message']['content']

def update_rss(title, filename, img_url, desc):
    print("LOG: Memperbarui rss.xml...")
    rss_file = "rss.xml"
    chosen_base = random.choice([GITHUB_BASE_URL, VERCEL_BASE_URL])
    post_link = f"{chosen_base}/posts/{filename}"
    
    new_item_str = f"""
    <item>
        <title>{title}</title>
        <link>{post_link}</link>
        <description>{desc}</description>
        <pubDate>{datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000')}</pubDate>
        <enclosure url="{img_url}" length="0" type="image/jpeg" />
        <guid>{post_link}</guid>
    </item>"""

    if not os.path.exists(rss_file) or os.stat(rss_file).st_size == 0:
        content = f'<?xml version="1.0" encoding="UTF-8" ?><rss version="2.0"><channel><title>Tier 1 Insights</title><link>{GITHUB_BASE_URL}</link><description>Daily Trends</description>{new_item_str}</channel></rss>'
    else:
        with open(rss_file, "r", encoding="utf-8") as f:
            content = f.read()
        if "</channel>" in content:
            content = content.replace("</channel>", f"{new_item_str}</channel>")
        else:
            content += f"\n{new_item_str}"

    with open(rss_file, "w", encoding="utf-8") as f:
        f.write(content)

def main():
    if not GROQ_API_KEY: 
        print("LOG ERROR: GROQ_API_KEY kosong!")
        sys.exit(1)
        
    try:
        news_title = get_trending_news()
        clean_title = news_title.split(" - ")[0].strip()
        
        # CEK DUPLIKAT
        if os.path.exists("index.html"):
            with open("index.html", "r", encoding="utf-8") as f:
                if clean_title[:20] in f.read(): # Cek 20 karakter pertama saja agar lebih akurat
                    print(f"LOG SKIP: Artikel '{clean_title}' sudah ada. Coba 'Run Workflow' lagi untuk judul lain.")
                    return 

        raw_text = generate_article_groq(news_title)
        title = re.search(r"\[TITLE\](.*)", raw_text, re.I).group(1).strip()
        desc = re.search(r"\[DESC\](.*)", raw_text, re.I).group(1).strip()
        content = re.search(r"\[CONTENT\](.*)\[IMG\]", raw_text, re.I|re.S).group(1).strip()
        img_p = re.search(r"\[IMG\](.*)", raw_text, re.I).group(1).strip()

        img_url = f"https://image.pollinations.ai/prompt/{img_p.replace(' ', '%20')}?width=800&height=600&nologo=true&seed={random.randint(1,9999)}"

        if not os.path.exists("posts"): os.makedirs("posts")
        filename = re.sub(r'[^a-zA-Z0-9]', '-', title.lower()).strip('-') + ".html"
        
        # Tulis artikel
        with open(f"posts/{filename}", "w", encoding="utf-8") as f:
            f.write(f"<!DOCTYPE html><html><head><title>{title}</title><link rel='stylesheet' href='../style.css'>{ADSTERRA_SOCIAL_BAR}</head><body><nav><a href='../index.html'>Home</a></nav><article><h1>{title}</h1><img src='{img_url}' style='width:100%;border-radius:10px;'><div class='content'>{content}</div><center><a href='{ADSTERRA_DIRECT_LINK}' class='cta-button' style='background:#007bff;color:white;padding:15px;text-decoration:none;border-radius:5px;'>READ MORE</a></center></article></body></html>")

        # Update RSS & Index
        update_rss(title, filename, img_url, desc)
        
        with open("index.html", "r", encoding="utf-8") as f:
            idx = f.read()
        
        new_li = f'<li><a href="posts/{filename}">{title}</a></li>\n'
        marker = '<!-- Script Bot akan otomatis menambah daftar artikel di sini -->'
        if marker in idx:
            new_idx = idx.replace(marker, f"{marker}\n{new_li}")
        else:
            new_idx = idx.replace("</ul>", f"{new_li}</ul>")
            
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(new_idx)

        print(f"LOG BERHASIL: '{title}' diterbitkan!")

    except Exception as e:
        print(f"LOG ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
