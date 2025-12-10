import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
import json

# ----------------------------------------------------
# Utility functions
# ----------------------------------------------------

def clean_text(text):
    """Clean multiple spaces, line breaks, etc."""
    return re.sub(r'\n\s*\n', '\n\n', text).strip()


def html_to_markdown(article):
    """Convert basic GFG HTML to clean Markdown/MDX."""
    md = []

    for tag in article.descendants:
        if tag.name in ["h1", "h2", "h3", "h4"]:
            level = {"h1": "#", "h2": "##", "h3": "###", "h4": "####"}[tag.name]
            md.append(f"{level} {tag.get_text(strip=True)}\n")

        elif tag.name == "p":
            md.append(tag.get_text(strip=True) + "\n")

        elif tag.name in ["ul", "ol"]:
            for li in tag.find_all("li", recursive=False):
                prefix = "-" if tag.name == "ul" else "1."
                md.append(f"{prefix} {li.get_text(strip=True)}")
            md.append("\n")

        elif tag.name == "pre":
            code_text = tag.get_text()
            md.append(f"``` \n{code_text}\n```\n")

    return clean_text("\n".join(md))

def estimate_read_time(text):
    word_count = len(text.split())
    minutes = max(1, word_count // 150)  # 150 wpm average
    return f"{minutes} min read"

# ----------------------------------------------------
# Detect article container
# ----------------------------------------------------
def get_article_container(soup):
    for cls in ["article--viewer", "content", "text"]:
        article = soup.find("div", class_=cls)
        if article:
            return article
    return None

# ----------------------------------------------------
# Extract title & description
# ----------------------------------------------------
def extract_title(article):
    h1 = article.find("h1")
    if h1:
        return h1.get_text(strip=True)
    return "Untitled Article"

def extract_description(article):
    p = article.find("p")
    if p:
        return p.get_text(strip=True)
    return "No description available."

# ----------------------------------------------------
# Auto-generate frontmatter
# ----------------------------------------------------
def build_frontmatter(url, title, description, markdown_content):
    # Extract subject/topic from URL
    parts = url.strip("/").split("/")
    subject = parts[-2] if len(parts) >= 2 else "general"
    topic = parts[-1].replace("-", " ")

    # Auto values
    chapter = title
    chapterOrder = 1
    category = "General"
    difficulty = "beginner"
    order = 1
    keywords = list(set(re.findall(r'\b[a-zA-Z]{4,}\b', markdown_content.lower())))[:12]
    relatedTopics = []
    relatedQuestions = []
    searchTags = title.lower().split()
    lastUpdated = datetime.now().strftime("%Y-%m-%d")
    metaDescription = description
    estimatedTime = estimate_read_time(markdown_content)
    prerequisites = []

    frontmatter = {
        "title": title,
        "description": description,
        "subject": subject,
        "topic": topic,
        "chapter": chapter,
        "chapterOrder": chapterOrder,
        "category": category,
        "difficulty": difficulty,
        "order": order,
        "keywords": keywords,
        "relatedTopics": relatedTopics,
        "relatedQuestions": relatedQuestions,
        "searchTags": searchTags,
        "lastUpdated": lastUpdated,
        "metaDescription": metaDescription,
        "estimatedTime": estimatedTime,
        "prerequisites": prerequisites
    }

    # Convert dict → YAML frontmatter
    yaml = "---\n"
    for key, value in frontmatter.items():
        if isinstance(value, list):
            yaml += f"{key}: {json.dumps(value)}\n"
        else:
            yaml += f"{key}: \"{value}\"\n"
    yaml += "---\n\n"

    return yaml

# ----------------------------------------------------
# Save MDX file
# ----------------------------------------------------
def save_mdx(content, filename):
    if not filename.endswith(".mdx"):
        filename += ".mdx"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"\n📄 Saved as {filename}")

# ----------------------------------------------------
# Main scraper
# ----------------------------------------------------
def main():
    print("📗 GeeksforGeeks → MDX Scraper (Auto Frontmatter)")
    url = input("\nEnter GeeksforGeeks article URL: ")

    headers = {"User-Agent": "Mozilla/5.0"}
    soup = BeautifulSoup(requests.get(url, headers=headers).text, "html.parser")

    article = get_article_container(soup)
    if not article:
        print("❌ Article content not found.")
        return

    # Extract
    title = extract_title(article)
    description = extract_description(article)
    markdown_content = html_to_markdown(article)

    # Build MDX frontmatter
    frontmatter = build_frontmatter(url, title, description, markdown_content)

    final_mdx = frontmatter + markdown_content

    print("\n=== PREVIEW OF MDX CONTENT ===\n")
    print(final_mdx[:800] + "\n...\n")

    filename = input("\nEnter file name (without extension): ")

    save_mdx(final_mdx, filename)

# Run program
if __name__ == "__main__":
    main()
