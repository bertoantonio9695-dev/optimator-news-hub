import os
import requests
from google import genai # Library terbaru
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

# Inisialisasi Client Baru sesuai saran Google
client = genai.Client(api_key=GEMINI_API_KEY)

def get_trending_news():
    print("Mengambil berita terbaru dari Google News USA RSS...")
    rss_url = "https://news.google.com/rss/search?q=finance+technology+usa&hl=en-US&gl=US&ceid=US:en"
    response = requests.get(rss_url)
    root = ET.fromstring(response.content)
    
    item = root.find('.//item')
    title = item.find('title').text
    return title

def generate_article(news_title):
    print(f"Menyusun artikel berdasarkan berita: {news_title}")
    prompt = f"""
    Write a 500-word professional blog post in English based on this news: '{news_title}'.
    Target audience: USA. 
    Format your response EXACTLY like this:
    [TITLE] Judul Disini
    [DESC] Deskripsi Singkat
    [CONTENT] Isi Artikel HTML (h2 dan p)
    [IMG] Deskripsi Gambar Pendek (max 5 kata)
    """
    # Cara panggil baru untuk library google-genai
    response = client.models.generate_content(
        model='gemini-1.5-flash',
        contents=prompt
    )
    return response.text

def main():
    try:
        news_title = get_trending_news()
        raw_text = generate_article(news_title)
        
        # Ekstraksi Data
        title = re.search(r"\[TITLE\](.*)", raw_text).group(1).strip()
        desc = re.search(r"\[DESC\](.*)", raw_text).group(1).strip()
        content_match = re.search(r"\[CONTENT\](.*)\[IMG\]", raw_text, re.DOTALL)
        content = content_match.group(1).strip() if content_match else raw_text
        img_prompt = re.search(r"\[IMG\](.*)", raw_text).group(1).strip()

        img_url = f"https://pollinations.ai/p/{img_prompt.replace(' ', '%20')}?width=800&height=600&seed={datetime.now().second}"

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

        print(f"BERHASIL: Artikel '{title}' terbit melalui library terbaru!")

    except Exception as e:
        print(f"FAILED PROCESS: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
