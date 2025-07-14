import os
import markdown2
import yaml

# --- Configuration ---
POEMS_DIR = '_poems'
OUTPUT_DIR = 'public'
SITE_TITLE = "The Collective Archive of cafiro"
AUTHOR_NAME = "cafiro"
ARTIST_NAME = "/cafiro/"

# --- HTML Templates ---
INDEX_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{site_title}</title>
    <link rel="stylesheet" href="style.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
</head>
<body>
    <header>
        <h1>{site_title}</h1>
    </header>
    <main>
        <h2>The Archive</h2>
        <ul class="poem-list">
            {poem_links}
        </ul>
    </main>
    <footer>
        <p>© 2025 {author_name}</p>
    </footer>
</body>
</html>
"""

POEM_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | {site_title}</title>
    <link rel="stylesheet" href="style.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
</head>
<body>
    <main class="poem-container">
        <a href="index.html" class="back-link">← Back to Archive</a>
        <h1 class="poem-title">{title}</h1>
        <div class="poem-body">
            {content}
        </div>
        <p class="artist-name">{artist_name}</p>
        <pre class="date-block">{date}</pre>
    </main>
    <footer>
        <p>© 2025 {author_name}</p>
    </footer>
</body>
</html>
"""

# --- Build Script Logic ---
def build_site():
    print("Starting site build...")
    poems_data = []
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    for filename in os.listdir(POEMS_DIR):
        if filename.endswith('.md'):
            filepath = os.path.join(POEMS_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                parts = content.split('---')
                if len(parts) >= 3:
                    metadata = yaml.safe_load(parts[1])
                    poem_md = '---'.join(parts[2:]).strip()
                    poem_html = markdown2.markdown(poem_md, extras=["break-on-newline"])
                    
                    metadata['content'] = poem_html
                    metadata['filename'] = filename.replace('.md', '.html')
                    poems_data.append(metadata)

    poems_data.sort(key=lambda p: str(p.get('date', '')), reverse=True)

    for poem in poems_data:
        page_content = POEM_TEMPLATE.format(
            title=poem.get('title', 'Untitled'),
            content=poem.get('content', ''),
            artist_name=ARTIST_NAME,
            date=poem.get('date', ''),
            site_title=SITE_TITLE,
            author_name=AUTHOR_NAME
        )
        with open(os.path.join(OUTPUT_DIR, poem['filename']), 'w', encoding='utf-8') as f:
            f.write(page_content)
        print(f"  - Built page for: {poem.get('title', 'Untitled')}")

    poem_links_html = ""
    for poem in poems_data:
        poem_links_html += f'<li><a href="{poem["filename"]}">{poem["title"]}</a></li>'
    
    index_content = INDEX_TEMPLATE.format(
        site_title=SITE_TITLE,
        author_name=AUTHOR_NAME,
        poem_links=poem_links_html
    )
    with open(os.path.join(OUTPUT_DIR, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(index_content)
    print("  - Built index.html")

    if os.path.exists('style.css'):
        os.system(f'cp style.css {OUTPUT_DIR}/style.css')
        print("  - Copied style.css")

    print("Site build complete!")

if __name__ == '__main__':
    build_site()