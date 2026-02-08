import os
from google import genai
from google.genai import types
from datetime import datetime
import re
import sys

# --- KONFIGURASI ---
ADSTERRA_SOCIAL_BAR = """<script src="https://pl28671543.effectivegatecpm.com/b4/04/60/b40460008fe491a20d7ed511234ef60c.js"></script>"""
ADSTERRA_DIRECT_LINK = "https://www.effectivegatecpm.com/scpufanss?key=91a5369ee9e711e8e1f77e2491d62f65"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("ERROR: GEMINI_API_KEY tidak ditemukan!")
    sys.exit(1)

# Inisialisasi Client (Versi 2.0)
client = genai.Client(api_key=GEMINI_API_KEY)

def generate_content():
    print("Mencari tren real-time dengan Gemini 2.0 Flash...")
    prompt = """
    Using Google Search, find a high-CPM trending topic in the USA TODAY. 
    Write a 500-word blog post in English. 
    Format strictly like this:
    [TITLE] Title Here
    [DESC] Brief Description
    [CONTENT] HTML Article Content
    [IMG] Short Image Description
    """
    
    try:
        # MENGGUNAKAN MODEL 2.0 FLASH (Terbaru & Paling Stabil)
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())]
            ),
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"API Error: {str(e)}")
        # Fallback jika model 2.0 belum tersedia di wilayah Anda, coba 1.5 kembali dengan nama berbeda
        print("Mencoba fallback ke model alternatif...")
        response = client.models.generate_content(model='gemini-1.5-flash', contents=prompt)
        return response.text

def main():
    try:
        raw_text = generate_content()
        
        # Ekstraksi Data menggunakan Regex yang lebih fleksibel
        title_search = re.search(r"\[TITLE\](.*)", raw_text)
        desc_search = re.search(r"\[DESC\](.*)", raw_text)
        content_search = re.search(r"\[CONTENT\](.*)\[IMG\]", raw_text, re.DOTALL)
        img_search = re.search(r"\[IMG\](.*)", raw_text)

        if not (title_search and desc_search and content_search and img_search):
            print("AI tidak mengikuti format. Menggunakan pembersihan teks manual...")
            title = "Trending Update " + datetime.now().strftime("%Y-%m-%d")
            desc = "Latest news and insights."
            content = raw_text
            img_prompt = "technology and finance"
        else:
            title = title_search.group(1).strip()
            desc = desc_search.group(1).strip()
            content = content_search.group(1).strip()
            img_prompt = img_search.group(1).strip()

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

        print(f"BERHASIL: Artikel '{title}' terbit.")

    except Exception as e:
        print(f"FAILED PROCESS: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
