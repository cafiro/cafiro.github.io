import os
import markdown2
import yaml
import re
import json
from html import unescape

# --- Configuration ---
POEMS_DIR = '_poems'
OUTPUT_DIR = 'public'
SITE_TITLE = "The Collective Archive Of cafiro"
AUTHOR_NAME = "cafiro"
ARTIST_NAME = "/cafiro/"
POEMS_PER_PAGE = 5

# Function to sanitize the title to be used in URLs
def sanitize_title(title):
    """Sanitize titles for URL compatibility"""
    return re.sub(r'[^a-zA-Z0-9\-]', '_', title).lower()

def generate_preview(poem_md_text, line_limit=6):
    lines = poem_md_text.strip().split('\n')
    preview_lines = lines[:line_limit]
    preview_md = '\n'.join(preview_lines)
    preview_html = markdown2.markdown(preview_md, extras=["break-on-newline"])
    if len(lines) > line_limit:
        preview_html += '<br><span class="ellipsis">...</span>'
    return preview_html

def get_sortable_date(date_string):
    match = re.search(r'\d{4}-\d{2}-\d{2}', str(date_string))
    return match.group(0) if match else '1970-01-01'

def strip_html_tags(html):
    text = re.sub('<[^<]+?>', '', html)
    return unescape(text).strip()

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
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=Lora:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
    <style>
        .search-sort-bar {{ display: flex; gap: 1em; margin-bottom: 2em; }}
        .search-input {{ flex: 1; padding: 0.5em; font-size: 1em; }}
        .sort-select {{ padding: 0.5em; font-size: 1em; }}
    </style>
</head>
<body>
    <header>
        <h1>{site_title}</h1>
    </header>
    <main>
        <div class="search-sort-bar">
            <input type="text" id="searchInput" class="search-input" placeholder="Search by name, content, or date...">
            <select id="sortSelect" class="sort-select">
                <option value="desc">Date: Newest First</option>
                <option value="asc">Date: Oldest First</option>
            </select>
        </div>
        <ul id="poemList" class="poem-list">
            {poem_links}
        </ul>
    </main>
    <footer>
        <p>© 2025 {author_name}</p>
    </footer>
    <script>
    const searchInput = document.getElementById('searchInput');
    const sortSelect = document.getElementById('sortSelect');
    const poemList = document.getElementById('poemList');
    let poems = Array.from(poemList.children);

    function filterAndSort() {{
        const query = searchInput.value.toLowerCase();
        const sortOrder = sortSelect.value;
        let filtered = poems.filter(li => {{
            const title = li.getAttribute('data-title').toLowerCase();
            const content = li.getAttribute('data-content').toLowerCase();
            const date = li.getAttribute('data-date');
            return title.includes(query) || content.includes(query) || date.includes(query);
        }});
        filtered.sort((a, b) => {{
            const dateA = a.getAttribute('data-date');
            const dateB = b.getAttribute('data-date');
            return sortOrder === 'asc' ? dateA.localeCompare(dateB) : dateB.localeCompare(dateA);
        }});
        poemList.innerHTML = '';
        filtered.forEach(li => poemList.appendChild(li));
    }}

    searchInput.addEventListener('input', filterAndSort);
    sortSelect.addEventListener('change', filterAndSort);
    </script>
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
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=Lora:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
    <style>
        body {{
            font-family: 'Lora', serif;
            line-height: 1.7;
            color: #333333;
            background-color: #fbfaf8;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}
        .poem-container {{
            width: 80%;
            max-width: 800px;
            padding: 2rem;
            background-color: white;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            border-radius: 8px;
            text-align: center;
        }}
        .back-link {{
            display: block;
            margin-bottom: 1.5rem;
            font-size: 1.1rem;
            text-decoration: none;
            color: #555;
        }}
        .poem-title {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
        }}
        .poem-body {{
            font-size: 1.2rem;
            margin-bottom: 2rem;
        }}
        .artist-name {{
            font-size: 1rem;
            color: #888;
        }}
        .date-block {{
            font-size: 0.9rem;
            color: #ccc;
        }}
        footer {{
            text-align: center;
            margin-top: 2rem;
        }}
    </style>
</head>
<body>
    <main class="poem-container">
        <a href="index.html" class="back-link">← Back to The Archive</a>
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

def generate_pagination_links(current_page, num_pages):
    """Generates HTML for pagination links."""
    # Don't show pagination if there's only one page
    if num_pages <= 1:
        return ""

    links = '<div class="pagination-links">'

    # Previous link
    if current_page > 0:
        prev_page_url = 'index.html' if current_page == 1 else f'page{current_page}.html'
        links += f'<a href="{prev_page_url}" class="prev-next">« Previous</a>'
    else:
        links += '<span class="prev-next disabled">« Previous</span>'

    # Page number links
    for i in range(num_pages):
        page_url = 'index.html' if i == 0 else f'page{i + 1}.html'
        if i == current_page:
            links += f'<span class="page-number current">{i + 1}</span>'
        else:
            links += f'<a href="{page_url}" class="page-number">{i + 1}</a>'

    # Next link
    if current_page < num_pages - 1:
        next_page_url = f'page{current_page + 2}.html'
        links += f'<a href="{next_page_url}" class="prev-next">Next »</a>'
    else:
        links += '<span class="prev-next disabled">Next »</span>'

    links += '</div>'
    return links


# --- Build Logic ---
def build_site():
    print("Starting site build...")
    poems_data = []
    poems_index = []

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
                    metadata['full_content'] = poem_html
                    metadata['preview_content'] = generate_preview(poem_md)

                    # Sanitize the title to be URL-safe
                    sanitized_title = sanitize_title(metadata.get('title', 'Untitled'))

                    metadata['filename'] = f"{sanitized_title}.html"  # Make sure filename is URL-safe
                    
                    # Ensure 'date' is a string for serialization
                    date_str = get_sortable_date(metadata.get('date', ''))
                    metadata['sort_date'] = date_str
                    poems_data.append(metadata)
                    
                    poems_index.append({
                        'title': metadata.get('title', 'Untitled'),
                        'preview': metadata['preview_content'],
                        'date': date_str,  # Store date as string
                        'filename': metadata['filename']
                    })

    poems_data.sort(key=lambda p: p['sort_date'], reverse=True)

    # Write the global search index to a JSON file
    with open(os.path.join(OUTPUT_DIR, 'poem-index.json'), 'w', encoding='utf-8') as f:
        json.dump(poems_index, f, ensure_ascii=False, indent=4)

    # Build individual poem pages
    for poem in poems_data:
        page_content = POEM_TEMPLATE.format(
            title=poem.get('title', 'Untitled'),
            content=poem.get('full_content', ''),
            artist_name=ARTIST_NAME,
            date=poem.get('date', ''),
            site_title=SITE_TITLE,
            author_name=AUTHOR_NAME
        )

        with open(os.path.join(OUTPUT_DIR, poem['filename']), 'w', encoding='utf-8') as f:
            f.write(page_content)

    # Build the index page
    poem_links = ''
    for poem in poems_index:
        poem_links += f"""
        <li data-title="{poem['title']}" data-content="{strip_html_tags(poem['preview'])}" data-date="{poem['date']}">
            <a href="{poem['filename']}">{poem['title']}</a> <small>{poem['date']}</small>
        </li>
        """

    index_content = INDEX_TEMPLATE.format(
        site_title=SITE_TITLE,
        author_name=AUTHOR_NAME,
        poem_links=poem_links
    )

    with open(os.path.join(OUTPUT_DIR, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(index_content)

    print("Site build complete!")


if __name__ == "__main__":
    build_site()

