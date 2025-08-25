import os
from jinja2 import Environment, FileSystemLoader

# --- Configuration ---
SITE_NAME = "Cafiro's Poems"
POEMS_PER_PAGE = 5
OUTPUT_DIR = "docs"  # Changed from 'public' to 'docs' for GitHub Pages
POEMS_DIR = "poems"

# --- Data Loading ---
def get_poems():
    """Reads all poem files and returns them as a list of dictionaries."""
    poems = []
    for filename in sorted(os.listdir(POEMS_DIR), reverse=True):
        if filename.endswith(".txt"):
            filepath = os.path.join(POEMS_DIR, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                lines = f.readlines()
                title = lines[0].strip()
                content = "".join(lines[1:]).strip()
                slug = os.path.splitext(filename)[0]
                poems.append({"title": title, "content": content, "slug": slug})
    return poems

# --- HTML Generation ---
def generate_site():
    """Generates the static HTML site."""
    poems = get_poems()
    env = Environment(loader=FileSystemLoader("templates"))

    # Create output directory if it doesn't exist
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # --- Generate Home/Index Pages (with Pagination) ---
    template = env.get_template("index.html")
    total_poems = len(poems)
    num_pages = (total_poems + POEMS_PER_PAGE - 1) // POEMS_PER_PAGE

    for page_num in range(num_pages):
        start_index = page_num * POEMS_PER_PAGE
        end_index = start_index + POEMS_PER_PAGE
        page_poems = poems[start_index:end_index]

        pagination = {
            "page": page_num + 1,
            "total_pages": num_pages,
            "has_prev": page_num > 0,
            "prev_num": page_num,
            "has_next": page_num < num_pages - 1,
            "next_num": page_num + 2,
        }

        # For the first page, the output is index.html
        if page_num == 0:
            output_path = os.path.join(OUTPUT_DIR, "index.html")
        else:
            page_dir = os.path.join(OUTPUT_DIR, f"page{page_num + 1}")
            if not os.path.exists(page_dir):
                os.makedirs(page_dir)
            output_path = os.path.join(page_dir, "index.html")
            
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(template.render(
                site_name=SITE_NAME,
                poems=page_poems,
                pagination=pagination
            ))

    # --- Generate Individual Poem Pages ---
    poem_template = env.get_template("poem.html")
    poems_output_dir = os.path.join(OUTPUT_DIR, "poems")
    if not os.path.exists(poems_output_dir):
        os.makedirs(poems_output_dir)

    for poem in poems:
        output_path = os.path.join(poems_output_dir, f"{poem['slug']}.html")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(poem_template.render(
                site_name=SITE_NAME,
                poem=poem
            ))

    print("Site generated successfully!")

# --- Main Execution ---
if __name__ == "__main__":
    # You'll need to create a 'templates' directory with the following files:
    
    # --- templates/base.html ---
    if not os.path.exists("templates"):
        os.makedirs("templates")
        
    with open("templates/base.html", "w", encoding="utf-8") as f:
        f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ site_name }}</title>
    <style>
        body { font-family: sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; background-color: #fdfdfd; color: #333; }
        header { text-align: center; margin-bottom: 40px; }
        header h1 { margin: 0; }
        a { color: #007bff; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .poem-list-item { margin-bottom: 30px; border-bottom: 1px solid #eee; padding-bottom: 20px; }
        .poem-list-item h2 { margin-top: 0; }
        .poem-content { white-space: pre-wrap; line-height: 1.6; }
        .pagination { text-align: center; margin-top: 40px; }
        .pagination a { margin: 0 10px; padding: 8px 16px; border: 1px solid #ddd; border-radius: 4px; }
        .poem-container { background-color: #fff; padding: 30px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
        .back-link { display: block; margin-bottom: 20px; }
    </style>
</head>
<body>
    <header>
        <h1><a href="/">{{ site_name }}</a></h1>
    </header>
    <main>
        {% block content %}{% endblock %}
    </main>
</body>
</html>""")

    # --- templates/index.html ---
    with open("templates/index.html", "w", encoding="utf-8") as f:
        f.write("""{% extends "base.html" %}
{% block content %}
    {% for poem in poems %}
    <article class="poem-list-item">
        <h2><a href="/poems/{{ poem.slug }}.html">{{ poem.title }}</a></h2>
        <div class="poem-content">
            {{ poem.content.split('\\n')[:4]|join('\\n') }}...
        </div>
    </article>
    {% endfor %}

    {% if pagination and pagination.total_pages > 1 %}
    <nav class="pagination">
        {% if pagination.has_prev %}
            {% if pagination.prev_num == 1 %}
                <a href="/">&laquo; Previous</a>
            {% else %}
                <a href="/page{{ pagination.prev_num }}/">&laquo; Previous</a>
            {% endif %}
        {% endif %}
        
        <span>Page {{ pagination.page }} of {{ pagination.total_pages }}</span>

        {% if pagination.has_next %}
            <a href="/page{{ pagination.next_num }}/">Next &raquo;</a>
        {% endif %}
    </nav>
    {% endif %}
{% endblock %}""")

    # --- templates/poem.html ---
    with open("templates/poem.html", "w", encoding="utf-8") as f:
        f.write("""{% extends "base.html" %}
{% block content %}
    <a href="/" class="back-link">&larr; Back to all poems</a>
    <article class="poem-container">
        <h2>{{ poem.title }}</h2>
        <div class="poem-content">
            {{ poem.content }}
        </div>
    </article>
{% endblock %}""")
    
    generate_site()
