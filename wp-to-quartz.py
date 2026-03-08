#!/usr/bin/env python3
"""
WordPress XML Export → Quartz Markdown Converter

Usage:
    python3 wp-to-quartz.py <path-to-wordpress-export.xml> [--live]

Dry run by default. Add --live to actually write files.
"""

import sys
import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import urlretrieve

from markdownify import markdownify as md

QUARTZ_CONTENT = Path(__file__).parent / "content" / "posts"
IMAGE_DIR = QUARTZ_CONTENT / "images"

WP_NAMESPACE = {
    "content": "http://purl.org/rss/1.0/modules/content/",
    "wp": "http://wordpress.org/export/1.2/",
    "dc": "http://purl.org/dc/elements/1.1/",
    "excerpt": "http://wordpress.org/export/1.2/excerpt/",
}


def slugify(title: str) -> str:
    slug = title.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


def html_to_markdown(html_content: str) -> str:
    if not html_content:
        return ""
    content = html_content.replace("\n\n", "<br><br>")
    result = md(content, heading_style="ATX", bullets="-", strip=["script", "style"])
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result.strip()


def download_image(url: str, dest_dir: Path) -> str | None:
    try:
        parsed = urlparse(url)
        filename = os.path.basename(parsed.path)
        if not filename:
            return None
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / filename
        if not dest_path.exists():
            urlretrieve(url, dest_path)
            print(f"  Downloaded: {filename}")
        return f"images/{filename}"
    except Exception as e:
        print(f"  Failed to download {url}: {e}")
        return None


def process_images_in_content(content: str, dest_dir: Path, live: bool) -> str:
    img_pattern = r'!\[([^\]]*)\]\((https?://[^)]+)\)'

    def replace_image(match):
        alt_text = match.group(1)
        url = match.group(2)
        if live:
            local_path = download_image(url, dest_dir)
            if local_path:
                return f"![{alt_text}]({local_path})"
        return match.group(0)

    return re.sub(img_pattern, replace_image, content)


def parse_attachments(channel) -> dict[str, str]:
    """Parse attachment items and return a map of URL -> attachment URL."""
    attachments = {}
    for item in channel.findall("item"):
        post_type = item.find("wp:post_type", WP_NAMESPACE)
        if post_type is None or post_type.text != "attachment":
            continue
        url_el = item.find("wp:attachment_url", WP_NAMESPACE)
        guid_el = item.find("guid")
        if url_el is not None and url_el.text:
            attachments[url_el.text] = url_el.text
            if guid_el is not None and guid_el.text:
                attachments[guid_el.text] = url_el.text
    return attachments


def download_attachments(attachments: dict[str, str], dest_dir: Path, live: bool) -> dict[str, str]:
    """Download all attachments and return a map of original URL -> local path."""
    url_map = {}
    unique_urls = set(attachments.values())
    for url in unique_urls:
        if live:
            local_path = download_image(url, dest_dir)
            if local_path:
                url_map[url] = local_path
        else:
            parsed = urlparse(url)
            filename = os.path.basename(parsed.path)
            print(f"  [DRY RUN] Would download: {filename}")
            url_map[url] = f"images/{filename}"

    for orig_url, attachment_url in attachments.items():
        if attachment_url in url_map:
            url_map[orig_url] = url_map[attachment_url]

    return url_map


def rewrite_urls_in_content(content: str, url_map: dict[str, str]) -> str:
    """Replace remote WordPress URLs with local paths in markdown content."""
    for remote_url, local_path in url_map.items():
        content = content.replace(remote_url, local_path)
    return content


def parse_export(xml_path: str):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    channel = root.find("channel")
    posts = []
    attachments = parse_attachments(channel)

    for item in channel.findall("item"):
        post_type = item.find("wp:post_type", WP_NAMESPACE)
        status = item.find("wp:status", WP_NAMESPACE)

        if post_type is None or post_type.text != "post":
            continue
        if status is None or status.text != "publish":
            continue

        title_el = item.find("title")
        title = title_el.text if title_el is not None and title_el.text else "Untitled"

        pub_date_el = item.find("wp:post_date", WP_NAMESPACE)
        pub_date = None
        if pub_date_el is not None and pub_date_el.text:
            try:
                pub_date = datetime.strptime(pub_date_el.text, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                pass

        content_el = item.find("content:encoded", WP_NAMESPACE)
        html_content = content_el.text if content_el is not None and content_el.text else ""

        tags = []
        categories = []
        for cat in item.findall("category"):
            domain = cat.get("domain", "")
            text = cat.text or ""
            if domain == "post_tag":
                tags.append(text)
            elif domain == "category" and text.lower() != "uncategorized":
                categories.append(text)

        posts.append({
            "title": title,
            "date": pub_date,
            "html": html_content,
            "tags": tags,
            "categories": categories,
        })

    return posts, attachments


def generate_frontmatter(post: dict) -> str:
    lines = ["---"]
    lines.append(f'title: "{post["title"]}"')
    if post["date"]:
        lines.append(f'created: {post["date"].strftime("%Y-%m-%d")}')
    all_tags = post["tags"] + post["categories"]
    if all_tags:
        lines.append("tags:")
        for tag in all_tags:
            lines.append(f"  - {tag.lower()}")
    lines.append("---")
    return "\n".join(lines)


def generate_filename(post: dict) -> str:
    slug = slugify(post["title"])
    if post["date"]:
        return f"{post['date'].strftime('%Y-%m-%d')}_{slug}.md"
    return f"{slug}.md"


def convert(xml_path: str, live: bool = False):
    print(f"Parsing: {xml_path}")
    posts, attachments = parse_export(xml_path)
    print(f"Found {len(posts)} published posts")
    print(f"Found {len(set(attachments.values()))} attachments\n")

    if not posts:
        print("No posts found. Check that the file is a valid WordPress export.")
        return

    if attachments:
        print("--- Attachments ---")
        url_map = download_attachments(attachments, IMAGE_DIR, live)
        print()
    else:
        url_map = {}

    print("--- Posts ---")
    for post in posts:
        filename = generate_filename(post)
        filepath = QUARTZ_CONTENT / filename

        markdown_content = html_to_markdown(post["html"])
        markdown_content = process_images_in_content(markdown_content, IMAGE_DIR, live)
        if url_map:
            markdown_content = rewrite_urls_in_content(markdown_content, url_map)
        frontmatter = generate_frontmatter(post)
        full_content = f"{frontmatter}\n\n{markdown_content}\n"

        if live:
            QUARTZ_CONTENT.mkdir(parents=True, exist_ok=True)
            filepath.write_text(full_content, encoding="utf-8")
            print(f"  Wrote: {filepath.relative_to(Path(__file__).parent)}")
        else:
            print(f"  [DRY RUN] Would write: content/posts/{filename}")
            print(f"    Title: {post['title']}")
            print(f"    Date: {post['date'].strftime('%Y-%m-%d') if post['date'] else 'none'}")
            print(f"    Tags: {', '.join(post['tags'] + post['categories']) or 'none'}")
            print(f"    Content length: {len(markdown_content)} chars")
            print()

    print(f"\n{'Wrote' if live else 'Would write'} {len(posts)} posts to content/posts/")
    attachments_count = len(set(attachments.values()))
    if attachments_count:
        print(f"{'Downloaded' if live else 'Would download'} {attachments_count} attachments to content/posts/images/")
    if not live:
        print("\nRun again with --live to actually write files.")


def main():
    args = sys.argv[1:]

    if not args or "--help" in args or "-h" in args:
        print(__doc__)
        return

    xml_path = args[0]
    live = "--live" in args

    if not os.path.exists(xml_path):
        print(f"File not found: {xml_path}")
        return

    convert(xml_path, live)


if __name__ == "__main__":
    main()
