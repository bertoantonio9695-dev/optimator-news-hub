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

def get_trending_news():
    print("1. Mengambil daftar berita terbaru dari Google News...")
    try:
        rss_url = "https://news.google.com/rss/search?q=finance+technology+usa&hl=en-US&gl=US&ceid=US:en"
        response = requests.get(rss_url, timeout=15)
        root = ET.fromstring(response.content)
        
        # Ambil semua item berita
        items = root.findall('.//item')
        
        if not items:
            return f"Global Finance Trends {datetime.now().strftime('%Y-%m-%d')}"
            
        # Pilih satu berita secara ACAK dari 10 berita teratas agar tidak duplikat
        selected_item = random.choice(items[:10]) 
        return selected_item.find('title').text
    except Exception as e:
        print(f"Gagal ambil RSS: {e}")
        return f"Market Insights {datetime.now().strftime('%Y-%m-%d')}"

def generate_article_groq(news_title):
    print(f"2. Menyusun artikel unik via Groq: {news_title}")
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    prompt = f"Write a unique 500-word professional blog post in English about: '{news_title}'. Format output strictly as: [TITLE] title [DESC] short description [CONTENT] html content [IMG] short image prompt"
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7 # Tambahkan variasi kreatif
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
        print("ERROR: GROQ_API_KEY tidak ditemukan!")
        sys.exit(1)

    try:
        news_title = get_trending_news()
        
        # --- SISTEM CEK DUPLIKAT ---
        # Membersihkan judul untuk pengecekan
        clean_news_title = news_title.split(" - ")[0].strip()
        
        if os.path.exists("index.html"):
            with open("index.html", "r", encoding="utf-8") as f:
                current_index = f.read()
            if clean_news_title in current_index:
                print(f"SKIP: Judul '{clean_news_title}' sudah ada di halaman depan. Menghindari duplikat.")
                return 

        raw_text = generate_article_groq(news_title)
        
        # Ekstraksi Data menggunakan Regex
        try:
            title = re.search(r"\[TITLE\](.*)", raw_text, re.I).group(1).strip()
            desc = re.search(r"\[DESC\](.*)", raw_text, re.I).group(1).strip()
            content = re.search(r"\[CONTENT\](.*)\[IMG\]", raw_text, re.I|re.S).group(1).strip()
            img_p = re.search(r"\[IMG\](.*)", raw_text, re.I).group(1).strip()
        except:
            # Jika AI gagal mengikuti format, gunakan data darurat
            title = clean_news_title
            desc = "Latest updates on high-value finance and tech trends."
            content = raw_text
            img_p = "business and technology"

        # --- GENERATE GAMBAR ---
        clean_img_p = re.sub(r'[^a-zA-Z0-9\s]', '', img_p)
        encoded_img_p = clean_img_p.replace(' ', '%20')
        # Seed acak agar gambar selalu baru
        img_url = f"https://image.pollinations.ai/prompt/{encoded_img_p}?width=800&height=600&nologo=true&seed={random.randint(1, 9999)}"

        # Buat folder posts jika belum ada
        if not os.path.exists("posts"):
            os.makedirs("posts")

        # Buat nama file yang ramah URL
        filename = re.sub(r'[^a-zA-Z0-9]', '-', title.lower()).strip('-') + ".html"
        filepath = f"posts/{filename}"
        
        # Template HTML Postingan
        html_post = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <link rel="stylesheet" href="../style.css">
    {ADSTERRA_SOCIAL_BAR}
</head>
<body>
    <nav><a href="../index.html">← Home</a></nav>
    <article>
        <h1>{title}</h1>
        <img src="{img_url}" alt="{title}" style="width:100%;max-height:500px;object-fit:cover;border-radius:12px;margin-bottom:20px;">
        <div class='article-content'>{content}</div>
        <br>
        <center>
            <a href='{ADSTERRA_DIRECT_LINK}' class='cta-button' style='display:inline-block;background-color:#007bff;color:white;padding:15px 30px;text-decoration:none;border-radius:8px;font-weight:bold;'>Discover More</a>
        </center>
    </article>
</body>
</html>"""
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_post)

        # Update index.html
        if os.path.exists("index.html"):
            with open("index.html", "r", encoding="utf-8") as f:
                index_content = f.read()
            
            new_link = f'<li><a href="{filepath}">{title}</a> - <small>{datetime.now().strftime("%Y-%m-%d")}</small></li>\n'
            marker = '<!-- Script Bot akan otomatis menambah daftar artikel di sini -->'
            
            if marker in index_content:
                new_index = index_content.replace(marker, marker + "\n" + new_link)
            else:
                new_index = index_content.replace("</ul>", new_link + "</ul>")
                
            with open("index.html", "w", encoding="utf-8") as f:
                f.write(new_index)

        print(f"BERHASIL: Artikel '{title}' telah diterbitkan.")

    except Exception as e:
        print(f"FAILED: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
