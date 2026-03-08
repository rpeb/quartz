#!/usr/bin/env python3
"""
Obsidian to Quartz Sync Script
Syncs files from Obsidian vault staging area to Quartz content folder

Usage:
    python3 sync-from-obsidian.py --folder      # Use staging folder
    python3 sync-from-obsidian.py --tag         # Use publish tag in frontmatter
    python3 sync-from-obsidian.py --folder --live  # Actually copy files
"""

import os
import shutil
import sys
import re
from pathlib import Path
from datetime import datetime

# Configuration
OBSIDIAN_VAULT = Path("/home/rpeb/Documents/vault")
QUARTZ_CONTENT = Path("/home/rpeb/repos/quartz/content")
STAGING_FOLDER = "staging"  # Folder in your vault for files to publish
PUBLISH_TAG = "publish"  # Tag to look for in frontmatter (without #)


def extract_frontmatter(content):
    """Extract YAML frontmatter from markdown content"""
    # Match content between --- markers at the start of file
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if match:
        return match.group(1)
    return None


def has_publish_tag(file_path):
    """Check if a markdown file has 'publish' in frontmatter tags"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        frontmatter = extract_frontmatter(content)
        if not frontmatter:
            return False
        
        # Look for tags in frontmatter
        # Supports multiple formats:
        # tags: [publish, other]
        # tags: publish
        # tags:
        #   - publish
        #   - other
        
        # Check for array format: tags: [publish, ...]
        array_match = re.search(r'tags:\s*\[(.*?)\]', frontmatter, re.MULTILINE)
        if array_match:
            tags = [tag.strip().strip('"\'') for tag in array_match.group(1).split(',')]
            return PUBLISH_TAG in tags
        
        # Check for list format:
        # tags:
        #   - publish
        list_match = re.search(r'tags:\s*\n((?:\s*-\s*.+\n?)+)', frontmatter, re.MULTILINE)
        if list_match:
            tags = re.findall(r'-\s*(\S+)', list_match.group(1))
            tags = [tag.strip('"\'') for tag in tags]
            return PUBLISH_TAG in tags
        
        # Check for single value: tags: publish
        single_match = re.search(r'tags:\s*(\S+)', frontmatter)
        if single_match:
            tag = single_match.group(1).strip('"\'')
            return tag == PUBLISH_TAG
        
        return False
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False


def get_files_to_publish(use_tag=False):
    """Get list of files to publish from Obsidian vault"""
    files_to_sync = []
    
    if use_tag:
        # Option 1: Find all .md files with 'publish' tag in frontmatter
        print(f"🔍 Scanning for files with 'tags: {PUBLISH_TAG}' in frontmatter...")
        for md_file in OBSIDIAN_VAULT.rglob("*.md"):
            # Skip hidden folders and templates
            if any(part.startswith('.') for part in md_file.parts):
                continue
            if has_publish_tag(md_file):
                files_to_sync.append(md_file)
    else:
        # Option 2: Get all files from staging folder
        staging_path = OBSIDIAN_VAULT / STAGING_FOLDER
        if not staging_path.exists():
            print(f"❌ Staging folder not found: {staging_path}")
            print(f"   Please create the folder or use --tag option instead.")
            return []
        
        print(f"🔍 Scanning staging folder: {staging_path}")
        for md_file in staging_path.rglob("*.md"):
            files_to_sync.append(md_file)
    
    return files_to_sync


def sync_files(files_to_sync, dry_run=True):
    """Copy files from Obsidian to Quartz"""
    if not files_to_sync:
        print("📭 No files found to publish")
        return
    
    print(f"\n📝 Found {len(files_to_sync)} file(s) to publish:")
    
    for source_file in files_to_sync:
        # Calculate relative path from vault root
        relative_path = source_file.relative_to(OBSIDIAN_VAULT)
        
        # If using staging folder, remove it from the path
        if relative_path.parts[0] == STAGING_FOLDER:
            relative_path = Path(*relative_path.parts[1:])
        
        # Destination path in Quartz
        dest_file = QUARTZ_CONTENT / relative_path
        
        # Create destination directory if it doesn't exist
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy file
        if dry_run:
            print(f"  [DRY RUN] Would copy:")
            print(f"    FROM: {source_file}")
            print(f"    TO:   {dest_file}")
        else:
            shutil.copy2(source_file, dest_file)
            print(f"  ✅ Copied: {relative_path}")


def print_usage():
    """Print usage instructions"""
    print("""
Usage:
    python3 sync-from-obsidian.py --folder         # Use staging folder (dry run)
    python3 sync-from-obsidian.py --tag            # Use #publish tag (dry run)
    python3 sync-from-obsidian.py --folder --live  # Actually copy files
    python3 sync-from-obsidian.py --tag --live     # Actually copy files
    """)


def main():
    """Main sync function"""
    # Parse command line arguments
    args = sys.argv[1:]
    
    if not args or "--help" in args or "-h" in args:
        print_usage()
        return
    
    use_tag = "--tag" in args
    use_folder = "--folder" in args
    live_mode = "--live" in args
    
    if not use_tag and not use_folder:
        print("❌ Error: Must specify either --folder or --tag")
        print_usage()
        return
    
    dry_run = not live_mode
    
    print("=" * 60)
    print("🔄 Obsidian → Quartz Sync Tool")
    print("=" * 60)
    print(f"📂 Obsidian Vault: {OBSIDIAN_VAULT}")
    print(f"📂 Quartz Content: {QUARTZ_CONTENT}")
    print(f"🏷️  Publish Tag: tags: {PUBLISH_TAG} (in frontmatter)")
    print(f"📁 Staging Folder: {STAGING_FOLDER}")
    
    if dry_run:
        print("\n⚠️  DRY RUN MODE - No files will be copied")
        print("   Add --live flag to actually copy files\n")
    else:
        print("\n✅ LIVE MODE - Files will be copied\n")
    
    # Check if vault exists
    if not OBSIDIAN_VAULT.exists():
        print(f"❌ Obsidian vault not found at: {OBSIDIAN_VAULT}")
        return
    
    method = "tag-based (frontmatter: tags: publish)" if use_tag else "folder-based (staging/)"
    print(f"📋 Method: {method}")
    
    # Get files to publish
    files_to_sync = get_files_to_publish(use_tag)
    
    # Sync files
    sync_files(files_to_sync, dry_run)
    
    print("\n" + "=" * 60)
    if not dry_run and files_to_sync:
        print("✅ Sync complete!")
        print("\n📝 Next steps:")
        print("   1. Review the copied files in /content/")
        print("   2. Run: npx quartz build --serve")
        print("   3. Test locally at http://localhost:8080")
        print("   4. Commit and push:")
        print("      git add content/")
        print("      git commit -m 'Publish: <description>'")
        print("      git push")
    elif dry_run:
        print("ℹ️  Dry run complete - no files were copied")
        print("   Review the output above, then add --live flag to sync")
    print("=" * 60)


if __name__ == "__main__":
    main()
