import os
import markdown2
import yaml
import re
from html import unescape

#test

# --- Configuration ---
POEMS_DIR = '_poems'
OUTPUT_DIR = 'public'
SITE_TITLE = "The Collective Archive Of cafiro"
AUTHOR_NAME = "cafiro"
ARTIST_NAME = "/cafiro/"
POEMS_PER_PAGE = 5

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
                    metadata['filename'] = filename.replace('.md', '.html')
                    metadata['sort_date'] = get_sortable_date(metadata.get('date', ''))
                    poems_data.append(metadata)

    poems_data.sort(key=lambda p: p['sort_date'], reverse=True)

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
        print(f"  - Built page for: {poem.get('title', 'Untitled')}")

    # Build paginated index pages
    num_pages = (len(poems_data) + POEMS_PER_PAGE - 1) // POEMS_PER_PAGE
    for page_num in range(num_pages):
        start_index = page_num * POEMS_PER_PAGE
        end_index = start_index + POEMS_PER_PAGE
        page_poems = poems_data[start_index:end_index]

        poem_links_html = ""
        for poem in page_poems:
            clean_text = strip_html_tags(poem['full_content']).replace('"', "'")
            poem_links_html += f"""
        <li class=\"poem-card\" data-title=\"{poem['title']}\" data-content=\"{clean_text}\" data-date=\"{poem['sort_date']}\">
            <h2 class=\"index-poem-title\"><a href=\"{poem['filename']}\">{poem['title']}</a></h2>
            <div class=\"poem-preview\">{poem['preview_content']}</div>
            <a href=\"{poem['filename']}\" class=\"read-more\">Read more →</a>
        </li>
        """

        pagination_html = generate_pagination_links(page_num, num_pages)

        index_content = INDEX_TEMPLATE.format(
            site_title=SITE_TITLE,
            author_name=AUTHOR_NAME,
            poem_links=poem_links_html,
            pagination_links=pagination_html
        )

        if page_num == 0:
            index_filename = 'index.html'
        else:
            index_filename = f'page{page_num + 1}.html'

        with open(os.path.join(OUTPUT_DIR, index_filename), 'w', encoding='utf-8') as f:
            f.write(index_content)
        print(f"  - Built index page: {index_filename}")

    if os.path.exists('style.css'):
        os.system(f'cp style.css {os.path.join(OUTPUT_DIR, "style.css")}')
        print("  - Copied style.css")

    print("Site build complete!")

if __name__ == '__main__':
    build_site()