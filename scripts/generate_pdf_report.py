"""
Claude Auto SEO — PDF Report Generator
Converts Markdown SEO reports to styled PDF documents.
Usage: python3 generate_pdf_report.py reports/seo-report-example.com-2026-03-16.md
"""

import sys
import os
import re
from datetime import datetime


def markdown_to_html(md_content: str) -> str:
    """Convert Markdown to basic HTML."""
    html = md_content

    # Headers
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)

    # Bold and italic
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)

    # Code blocks
    html = re.sub(r'```[\w]*\n(.*?)```', r'<pre><code>\1</code></pre>', html, flags=re.DOTALL)
    html = re.sub(r'`(.+?)`', r'<code>\1</code>', html)

    # Tables
    def convert_table(match):
        lines = match.group(0).strip().split('\n')
        result = '<table>\n'
        for i, line in enumerate(lines):
            if re.match(r'^\|[-\s|]+\|$', line.strip()):
                continue
            cells = [c.strip() for c in line.strip('|').split('|')]
            tag = 'th' if i == 0 else 'td'
            result += '<tr>' + ''.join(f'<{tag}>{c}</{tag}>' for c in cells) + '</tr>\n'
        result += '</table>\n'
        return result

    html = re.sub(r'(\|.+\|\n)+', convert_table, html)

    # Bullet lists
    html = re.sub(r'(?m)^[-*] (.+)$', r'<li>\1</li>', html)
    html = re.sub(r'(<li>.*</li>\n?)+', r'<ul>\g<0></ul>', html)

    # Checkboxes
    html = html.replace('- [x]', '✅').replace('- [X]', '✅').replace('- [ ]', '☐')

    # Emojis and score bars pass through

    # Paragraphs
    lines = html.split('\n')
    result_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith('<'):
            line = f'<p>{stripped}</p>'
        result_lines.append(line)
    html = '\n'.join(result_lines)

    return html


def generate_html_report(md_content: str, output_path: str) -> str:
    """Generate a full styled HTML report."""
    body = markdown_to_html(md_content)

    # Extract title from first H1
    title_match = re.search(r'<h1>(.*?)</h1>', body)
    title = title_match.group(1) if title_match else "SEO Report"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
    font-size: 14px;
    line-height: 1.6;
    color: #1a1a2e;
    background: #f8f9fc;
  }}
  .cover {{
    background: linear-gradient(135deg, #0f3460 0%, #16213e 50%, #0f3460 100%);
    color: white;
    padding: 80px 60px;
    min-height: 300px;
    page-break-after: always;
  }}
  .cover h1 {{
    font-size: 2.5em;
    font-weight: 800;
    margin-bottom: 16px;
    color: white;
    border: none;
  }}
  .cover .subtitle {{ font-size: 1.1em; opacity: 0.85; margin-bottom: 8px; }}
  .cover .meta {{ font-size: 0.9em; opacity: 0.7; margin-top: 24px; }}
  .cover .badge {{
    display: inline-block;
    background: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.3);
    border-radius: 20px;
    padding: 4px 16px;
    font-size: 0.85em;
    margin-top: 16px;
  }}
  .content {{ max-width: 900px; margin: 0 auto; padding: 40px 60px; background: white; }}
  h1 {{ font-size: 2em; color: #0f3460; border-bottom: 3px solid #e74c3c; padding-bottom: 12px; margin: 32px 0 16px; }}
  h2 {{ font-size: 1.5em; color: #16213e; border-left: 4px solid #e74c3c; padding-left: 12px; margin: 28px 0 12px; }}
  h3 {{ font-size: 1.15em; color: #0f3460; margin: 20px 0 8px; }}
  p {{ margin-bottom: 12px; color: #333; }}
  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 16px 0;
    font-size: 13px;
  }}
  th {{
    background: #0f3460;
    color: white;
    padding: 10px 12px;
    text-align: left;
    font-weight: 600;
  }}
  td {{ padding: 8px 12px; border-bottom: 1px solid #e8eaf0; }}
  tr:nth-child(even) td {{ background: #f8f9fc; }}
  ul {{ padding-left: 24px; margin: 12px 0; }}
  li {{ margin-bottom: 6px; color: #333; }}
  code {{
    background: #f0f2f8;
    padding: 2px 6px;
    border-radius: 3px;
    font-family: 'Courier New', monospace;
    font-size: 12px;
    color: #e74c3c;
  }}
  pre {{
    background: #1a1a2e;
    color: #e8eaf0;
    padding: 20px;
    border-radius: 8px;
    overflow-x: auto;
    margin: 16px 0;
  }}
  pre code {{ background: none; color: inherit; padding: 0; }}
  .score-box {{
    background: linear-gradient(135deg, #0f3460, #16213e);
    color: white;
    border-radius: 12px;
    padding: 24px;
    text-align: center;
    margin: 24px 0;
  }}
  .score-box .score {{ font-size: 3em; font-weight: 800; }}
  .score-box .label {{ font-size: 0.9em; opacity: 0.8; }}
  strong {{ color: #0f3460; }}
  em {{ color: #555; }}
  .footer {{
    text-align: center;
    color: #888;
    font-size: 12px;
    padding: 20px;
    border-top: 1px solid #e8eaf0;
    margin-top: 40px;
  }}
  @media print {{
    .cover {{ page-break-after: always; }}
    h2 {{ page-break-before: auto; }}
    table {{ page-break-inside: avoid; }}
  }}
</style>
</head>
<body>
<div class="cover">
  <h1>🚀 Claude Auto SEO</h1>
  <div class="subtitle">{title}</div>
  <div class="meta">Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}</div>
  <div class="badge">Claude Auto SEO v1.0</div>
</div>
<div class="content">
{body}
<div class="footer">
  Generated by Claude Auto SEO — github.com/YOUR_USERNAME/claude-auto-seo
</div>
</div>
</body>
</html>"""

    html_path = output_path.replace('.pdf', '.html').replace('.md', '.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)

    return html_path


def generate_pdf(md_path: str) -> str:
    """Convert a Markdown report to PDF."""
    if not os.path.exists(md_path):
        print(f"Error: File not found: {md_path}")
        sys.exit(1)

    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    pdf_path = md_path.replace('.md', '.pdf')
    html_path = generate_html_report(md_content, pdf_path)

    # Try WeasyPrint first (best quality)
    try:
        from weasyprint import HTML, CSS
        HTML(filename=html_path).write_pdf(pdf_path)
        os.remove(html_path)
        print(f"✅ PDF generated: {pdf_path}")
        return pdf_path
    except ImportError:
        pass

    # Fallback to pdfkit
    try:
        import pdfkit
        pdfkit.from_file(html_path, pdf_path)
        os.remove(html_path)
        print(f"✅ PDF generated: {pdf_path}")
        return pdf_path
    except ImportError:
        pass

    # Final fallback — keep HTML
    print(f"⚠️  PDF libraries not installed. HTML report saved: {html_path}")
    print("   Install WeasyPrint: pip install weasyprint")
    return html_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 generate_pdf_report.py <path-to-report.md>")
        sys.exit(1)

    result = generate_pdf(sys.argv[1])
    print(f"Report ready: {result}")
