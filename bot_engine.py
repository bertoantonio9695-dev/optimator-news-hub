import os
import requests
import google.generativeai as genai
from datetime import datetime
import re
import sys

# --- KONFIGURASI ---
ADSTERRA_SOCIAL_BAR = """<script src="https://pl28671543.effectivegatecpm.com/b4/04/60/b40460008fe491a20d7ed511234ef60c.js"></script>"""
ADSTERRA_DIRECT_LINK = "https://www.effectivegatecpm.com/scpufanss?key=91a5369ee9e711e8e1f77e2491d62f65"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("ERROR: GEMINI_API_KEY tidak ditemukan di Secrets!")
    sys.exit(1)

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    tools=[{ "google_search_retrieval": {} }] 
)

def generate_content():
    prompt = """
    Search for a trending high-CPM news in the USA today (Finance/Tech). 
    Write a blog post in English. 
    Format your response EXACTLY like this:
    [TITLE] Judul Disini
    [DESC] Deskripsi Singkat
    [CONTENT] Isi Artikel HTML
    [IMG] Deskripsi Gambar
    """
    response = model.generate_content(prompt)
    return response.text

def main():
    try:
        raw_text = generate_content()
        
        # Ekstraksi dengan metode yang lebih aman
        title = re.search(r"\[TITLE\](.*)", raw_text).group(1).strip()
        desc = re.search(r"\[DESC\](.*)", raw_text).group(1).strip()
        content = re.search(r"\[CONTENT\](.*)\[IMG\]", raw_text, re.DOTALL).group(1).strip()
        img_prompt = re.search(r"\[IMG\](.*)", raw_text).group(1).strip()

        # Gambar
        img_url = f"https://pollinations.ai/p/{img_prompt.replace(' ', '%20')}?width=800&height=600&seed={datetime.now().second}"

        # Buat Folder posts jika belum ada
        if not os.path.exists("posts"):
            os.makedirs("posts")

        # Simpan Postingan Baru
        filename = re.sub(r'[^a-zA-Z0-9]', '-', title.lower()).strip('-') + ".html"
        filepath = f"posts/{filename}"
        
        html_post = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>{title}</title><link rel="stylesheet" href="../style.css">{ADSTERRA_SOCIAL_BAR}</head><body><nav><a href="../index.html">Home</a></nav><article><h1>{title}</h1><img src="{img_url}" style="width:100%"><div class='article-content'>{content}</div><br><center><a href='{ADSTERRA_DIRECT_LINK}' class='cta-button'>Learn More</a></center></article></body></html>"""
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_post)

        # Update index.html (Menambahkan link di atas)
        with open("index.html", "r", encoding="utf-8") as f:
            index_content = f.read()
        
        new_link = f'<li><a href="{filepath}">{title}</a> - <small>{datetime.now().strftime("%Y-%m-%d")}</small></li>\n'
        marker = '<!-- Script Bot akan otomatis menambah daftar artikel di sini -->'
        
        new_index = index_content.replace(marker, marker + "\n" + new_link)
        
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(new_index)

        print(f"BERHASIL: {title}")

    except Exception as e:
        print(f"FAILED PROCESS: {e}")
        sys.exit(1) # Memaksa GitHub Action menunjukkan warna merah jika gagal

if __name__ == "__main__":
    main()
