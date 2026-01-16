# Obsidian to Quartz Sync Tool

Automates syncing of notes from your Obsidian vault to your Quartz site.

## Setup

### 1. Create Staging Area in Obsidian

**Option A: Use a Staging Folder**
- Create a folder called `staging/` in your Obsidian vault
- Move notes you want to publish into this folder
- Folder structure will be preserved when syncing

**Option B: Use Tags**
- Add `publish` to the tags in frontmatter of any note you want to publish
- Works from anywhere in your vault
- More flexible but requires tagging

Example frontmatter:
```yaml
---
title: My Post
tags: [publish, poetry]
---
```

Or:
```yaml
---
title: My Post
tags:
  - publish
  - poetry
---
```

### 2. Configure the Script

The script is already configured with your paths:
- **Obsidian Vault:** `/Users/prakashd/Documents/Obsidian/MacVault`
- **Quartz Content:** `/Users/prakashd/github/quartz/content`

Edit `sync-from-obsidian.py` if you need to change:
- `STAGING_FOLDER` - name of staging folder (default: "staging")
- `PUBLISH_TAG` - tag to look for in frontmatter (default: "publish")

## Usage

### Quick Start

```bash
cd /Users/prakashd/github/quartz

# Test with staging folder (dry run)
python3 sync-from-obsidian.py --folder

# Test with tags (dry run)
python3 sync-from-obsidian.py --tag

# Actually sync files from staging folder
python3 sync-from-obsidian.py --folder --live

# Actually sync files with #publish tag
python3 sync-from-obsidian.py --tag --live
```

### Step 1: Test Run (Dry Run)

First, test what will be synced without actually copying:

```bash
cd /Users/prakashd/github/quartz

# For folder-based:
python3 sync-from-obsidian.py --folder

# For tag-based:
python3 sync-from-obsidian.py --tag
```

This will show you which files would be copied.

### Step 2: Run Live Sync

Once you're happy with the dry run output:

```bash
# Add --live flag to actually copy files
python3 sync-from-obsidian.py --folder --live
```

### Step 4: Test & Publish

```bash
# Test locally
npx quartz build --serve

# Visit http://localhost:8080 to preview

# If everything looks good, publish
git add content/
git commit -m "Publish: weekly update"
git push
```

## Weekly Workflow

```bash
# 1. Write in Obsidian all week
# 2. Move finished notes to staging/ folder (or add tags: publish to frontmatter)
# 3. Once a week, run sync:

cd /Users/prakashd/github/quartz
python3 sync-from-obsidian.py --folder --live  # or --tag --live

# 4. Review and publish
npx quartz build --serve  # Test locally
git add content/
git commit -m "Publish: week of Jan 16"
git push
```

## Features

✅ **Two sync methods** - folder-based or frontmatter tag-based
✅ **Dry run mode** - test before syncing
✅ **Preserves structure** - maintains folder hierarchy
✅ **Safe copying** - uses copy not move (originals stay in Obsidian)
✅ **Detailed logging** - see exactly what's being synced
✅ **Frontmatter parsing** - looks for `tags: publish` in YAML frontmatter

## Tips

- Keep private notes outside the staging folder
- Use frontmatter to control metadata
- Add `tags: [publish]` or `tags: publish` to notes you want to publish
- Test locally before pushing to GitHub
- Can run sync multiple times safely (overwrites existing files)

## Troubleshooting

**"Staging folder not found"**
- Create `/Users/prakashd/Documents/Obsidian/MacVault/staging/` folder in Obsidian
- Or use tag-based method instead

**"No files found"**
- Make sure files are in staging folder or have `tags: publish` in frontmatter
- Check file paths in script output
- Verify frontmatter format (YAML between --- markers)

**Permission errors**
- Run: `chmod +x sync-from-obsidian.py`
