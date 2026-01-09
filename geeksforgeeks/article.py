import requests
from bs4 import BeautifulSoup
from fpdf import FPDF
from docx import Document
import os

# Ensure these paths are correct for your environment
# These TrueType fonts (.ttf) are required to render Unicode characters correctly
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

def fetch_article(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    res = requests.get(url, headers=headers)
    res.raise_for_status()

    soup = BeautifulSoup(res.text, "html.parser")
    title_tag = soup.find("h1")
    title = title_tag.get_text(strip=True) if title_tag else "GeeksforGeeks Article"
    
    # Updated selectors to better capture the main article body
    article = soup.find("div", class_="article-body") or soup.find("div", class_="text")

    return title, article

def parse_blocks(article):
    blocks = []
    if not article:
        return blocks

    for tag in article.find_all(["h2", "h3", "p", "pre", "ul"], recursive=True):
        if tag.name in ["h2", "h3"]:
            blocks.append(("heading", tag.get_text(strip=True)))
        elif tag.name == "p":
            text = tag.get_text(" ", strip=True)
            if text:
                blocks.append(("paragraph", text))
        elif tag.name == "pre":
            code = tag.get_text()
            if code.strip():
                blocks.append(("code", code))
        elif tag.name == "ul":
            for li in tag.find_all("li", recursive=False):
                text = li.get_text(" ", strip=True)
                if text:
                    blocks.append(("list", text))

    return blocks

def save_pdf(title, blocks, filename):
    # Initialize PDF with Unicode support enabled
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Register Unicode-capable fonts
    # If these files are missing, FPDF will default to Latin-1 and show '?'
    try:
        pdf.add_font("DejaVu", "", FONT_REGULAR)
        pdf.add_font("DejaVu", "B", FONT_BOLD)
        pdf.add_font("DejaVuMono", "", FONT_MONO)
        font_style = "DejaVu"
        mono_style = "DejaVuMono"
    except Exception as e:
        print(f"Font loading failed: {e}. Falling back to standard fonts.")
        pdf.set_font("Helvetica", "B", 18)
        font_style = "Helvetica"
        mono_style = "Courier"

    # Title
    pdf.set_font(font_style, "B", 18)
    pdf.multi_cell(0, 10, title)
    pdf.ln(4)

    # Pre-calculate usable width for multi_cell to avoid horizontal space errors
    usable_width = pdf.w - 2 * pdf.l_margin

    for kind, text in blocks:
        if kind == "heading":
            pdf.set_font(font_style, "B", 14)
            pdf.ln(4)
            pdf.multi_cell(0, 9, text)
            pdf.ln(2)

        elif kind == "paragraph":
            pdf.set_font(font_style, "", 11)
            pdf.multi_cell(0, 7, text)
            pdf.ln(2)

        elif kind == "list":
            pdf.set_font(font_style, "", 11)
            pdf.set_x(pdf.l_margin + 10) # Indentation
            # Explicitly set width to avoid 'Not enough horizontal space' error
            pdf.multi_cell(usable_width - 10, 7, f"• {text}")
            pdf.ln(1)

        elif kind == "code":
            pdf.set_font(mono_style, "", 9)
            pdf.set_fill_color(240, 240, 240)
            pdf.multi_cell(0, 5, text, fill=True)
            pdf.ln(3)

    pdf.output(filename)

def save_docx(title, blocks, filename):
    doc = Document()
    doc.add_heading(title, level=1)

    for kind, text in blocks:
        if kind == "heading":
            doc.add_heading(text, level=2)
        elif kind == "paragraph":
            doc.add_paragraph(text)
        elif kind == "list":
            doc.add_paragraph(text, style="List Bullet")
        elif kind == "code":
            para = doc.add_paragraph()
            run = para.add_run(text)
            run.font.name = "Courier New"

    doc.save(filename)

def main():
    url = input("Enter GeeksforGeeks article URL: ").strip()
    output = input("Choose format (pdf / docx): ").strip().lower()

    try:
        title, article = fetch_article(url)
        if not article:
            print("Could not find article content.")
            return

        blocks = parse_blocks(article)
        
        # Clean filename for the OS
        safe_name = "".join([c for c in title if c.isalnum() or c in (' ', '_')]).rstrip().replace(" ", "_")

        if output == "pdf":
            save_pdf(title, blocks, f"{safe_name}.pdf")
            print(f"PDF generated: {safe_name}.pdf")
        elif output == "docx":
            save_docx(title, blocks, f"{safe_name}.docx")
            print(f"DOCX generated: {safe_name}.docx")
        else:
            print("Invalid format.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()