import os
import requests
import google.generativeai as genai
from datetime import datetime
import re

# --- 1. KONFIGURASI (Ganti bagian ini) ---
# Masukkan kode iklan Adsterra Anda di bawah ini
ADSTERRA_SOCIAL_BAR = """<!-- Masukkan Kode Social Bar Adsterra Anda di Sini -->"""
ADSTERRA_DIRECT_LINK = "https://www.yourdirectlink.com" # Ganti dengan Direct Link Anda

# --- 2. SETTING GEMINI DENGAN SEARCH REAL-TIME ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Menggunakan Gemini 1.5 Flash (Gratis & Mendukung Search Grounding)
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    tools=[{ "google_search_retrieval": {} }] 
)

def generate_content():
    print("Sedang mencari berita tren dan menulis artikel...")
    prompt = """
    Search for the most recent and trending high-CPM topics in the USA today (related to Finance, Tech, or Health).
    Write a 500-word SEO-friendly blog post for a Tier 1 audience.
    Format the response EXACTLY like this:
    TITLE: [Title]
    DESCRIPTION: [Meta Description]
    CONTENT: [Article in HTML format with <h2> and <p> tags]
    IMAGE_PROMPT: [Description for a realistic photo]
    """
    response = model.generate_content(prompt)
    return response.text

def create_image(image_prompt):
    # Menggunakan Pollinations.ai (Gratis, Unik, Real-time)
    prompt_encoded = re.sub(r'[^a-zA-Z0-9]', '%20', image_prompt)
    image_url = f"https://pollinations.ai/p/{prompt_encoded}?width=800&height=600&seed={datetime.now().second}"
    return image_url

def save_post(title, content, image_url, description):
    # Buat folder posts jika belum ada
    if not os.path.exists("posts"):
        os.makedirs("posts")
        
    filename = re.sub(r'[^a-zA-Z0-9]', '-', title.lower()).strip('-') + ".html"
    filepath = f"posts/{filename}"
    
    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <meta name="description" content="{description}">
        <link rel="stylesheet" href="../style.css">
        {ADSTERRA_SOCIAL_BAR}
    </head>
    <body>
        <nav><a href="../index.html">← Back to Home</a></nav>
        <article>
            <h1>{title}</h1>
            <p><small>Published on: {datetime.now().strftime('%Y-%B-%d')}</small></p>
            <img src="{image_url}" alt="{title}" style="width:100%; border-radius:12px; margin-bottom:20px;">
            <div class="article-content">{content}</div>
            <div style="text-align:center; margin-top:40px; padding:20px; background:#eef2f7; border-radius:10px;">
                <h3>Recommended for you:</h3>
                <a href="{ADSTERRA_DIRECT_LINK}" class="cta-button">Click to Discover More</a>
            </div>
        </article>
    </body>
    </html>
    """
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_template)
    return filepath

def update_index():
    posts = []
    if os.path.exists("posts"):
        for file in os.listdir("posts"):
            if file.endswith(".html"):
                title = file.replace("-", " ").replace(".html", "").title()
                posts.append({"url": f"posts/{file}", "title": title})
    
    # Urutkan dari yang terbaru (berdasarkan file history)
    posts.reverse()
    
    links_html = "".join([f'<li><a href="{p["url"]}">{p["title"]}</a></li>' for p in posts])
    
    index_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Trending Insights - USA Daily</title>
        <link rel="stylesheet" href="style.css">
        {ADSTERRA_SOCIAL_BAR}
    </head>
    <body>
        <header><h1>Trending Daily Insights</h1><p>The latest from USA Tier 1 Markets</p></header>
        <main>
            <h2>Latest Stories</h2>
            <ul>{links_html}</ul>
        </main>
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(index_template)

if __name__ == "__main__":
    try:
        raw_data = generate_content()
        # Ekstrak data menggunakan regex
        title = re.search(r"TITLE: (.*)", raw_data).group(1)
        desc = re.search(r"DESCRIPTION: (.*)", raw_data).group(1)
        content = re.search(r"CONTENT: (.*)", raw_data, re.DOTALL).group(1).split("IMAGE_PROMPT:")[0]
        img_prompt = re.search(r"IMAGE_PROMPT: (.*)", raw_data).group(1)
        
        url_img = create_image(img_prompt)
        save_post(title, content, url_img, desc)
        update_index()
        print(f"SUKSES: Artikel '{title}' telah dipublish!")
    except Exception as e:
        print(f"ERROR: {e}")
