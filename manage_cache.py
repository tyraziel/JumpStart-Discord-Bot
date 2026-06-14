#!/usr/bin/env python3
"""
Cache management CLI for JumpStart Discord Bot.

AIA EAI Hin R Claude Code [Sonnet 4.6] v1.0

Usage:
    python manage_cache.py create-directories
    python manage_cache.py build-cache {images,decks} [--force]
    python manage_cache.py inspect-cache {images,decks,scryfall}
    python manage_cache.py purge-cache {images,decks,scryfall}
    python manage_cache.py backup-cache {images,decks,scryfall} [--output PATH]
    python manage_cache.py import-cache {images,decks,scryfall} BACKUP_FILE [--force]
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.parse
import zipfile
from datetime import datetime

import requests
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import jumpstartdata as jsd
from bot_cache import (
    BotCache,
    DECK_CACHE_DIR,
    IMAGE_CACHE_DIR,
    REQUEST_HEADERS,
    SCRYFALL_JSON_CACHE_DIR,
)

BACKUP_DIR = 'cache/backups'

ALL_CACHE_DIRS = [SCRYFALL_JSON_CACHE_DIR, IMAGE_CACHE_DIR, DECK_CACHE_DIR, BACKUP_DIR]

CACHE_TYPE_DIRS = {
    'images':   IMAGE_CACHE_DIR,
    'decks':    DECK_CACHE_DIR,
    'scryfall': SCRYFALL_JSON_CACHE_DIR,
}

# Rarity → number of deck list variants per theme
RARITY_VARIANTS = {
    'M': 1,
    'R': 2,
    'S': 2,
    'C': 4,
    'U': 1,
}


def _safe_filename(jset, name):
    return re.sub(r'[^\w\-]', '_', f"{jset}-{name}")


def _all_theme_entries():
    """Yield (set, theme_base_name) for every unique theme (one per rarity entry)."""
    for entry in jsd.jumpstart:
        yield entry['Set'], entry['Theme']


def _all_deck_variants():
    """Yield (set, variant_name) for every deck list file that should exist on GitHub."""
    for entry in jsd.jumpstart:
        jset = entry['Set']
        theme = entry['Theme']
        count = RARITY_VARIANTS.get(entry.get('Rarity', 'M'), 1)
        if count == 1:
            yield jset, theme
        else:
            for n in range(1, count + 1):
                yield jset, f"{theme} ({n})"


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_create_directories(args):
    print("Creating cache directories:")
    for d in ALL_CACHE_DIRS:
        os.makedirs(d, exist_ok=True)
        print(f"  {d}/")
    print("Done.")


def cmd_build_cache(args):
    if args.type == 'images':
        _build_images(args.force)
    else:
        _build_decks(args.force)


def _build_images(force):
    """Fetch Scryfall card images for every theme front card."""
    os.makedirs(IMAGE_CACHE_DIR, exist_ok=True)
    os.makedirs(SCRYFALL_JSON_CACHE_DIR, exist_ok=True)

    cache = BotCache()
    themes = list(_all_theme_entries())
    total = len(themes)
    fetched = skipped = failed = 0

    print(f"Building image cache for {total} themes (1s delay between Scryfall calls)...\n")

    for i, (jset, theme) in enumerate(themes, 1):
        key = _safe_filename(jset, theme)
        img_path = os.path.join(IMAGE_CACHE_DIR, key + '.png')
        json_path = os.path.join(SCRYFALL_JSON_CACHE_DIR, key + '.json')

        if not force and os.path.exists(img_path) and os.path.exists(json_path):
            print(f"  [{i:3}/{total}] SKIP  {jset} - {theme}")
            skipped += 1
            continue

        print(f"  [{i:3}/{total}] FETCH {jset} - {theme}", end='', flush=True)

        if force:
            for p in (img_path, json_path):
                if os.path.exists(p):
                    os.remove(p)

        img = cache.fetchThemeImageWithCacheScryfallCardImage(jset, theme)

        if img.size == (1, 1):
            print("  FAILED")
            failed += 1
        else:
            size_kb = os.path.getsize(img_path) // 1024 if os.path.exists(img_path) else 0
            print(f"  OK ({size_kb} KB)")
            fetched += 1


    print(f"\nDone. fetched={fetched}  skipped={skipped}  failed={failed}")


def _build_decks(force):
    """Fetch GitHub deck list JSONs for every theme variant."""
    os.makedirs(DECK_CACHE_DIR, exist_ok=True)

    variants = list(_all_deck_variants())
    total = len(variants)
    fetched = skipped = failed = 0

    print(f"Building deck cache for {total} deck variants...\n")

    for i, (jset, variant) in enumerate(variants, 1):
        key = _safe_filename(jset, variant)
        deck_path = os.path.join(DECK_CACHE_DIR, key + '.json')

        if not force and os.path.exists(deck_path):
            print(f"  [{i:3}/{total}] SKIP  {jset} - {variant}")
            skipped += 1
            continue

        print(f"  [{i:3}/{total}] FETCH {jset} - {variant}", end='', flush=True)

        #Fixing GitHub filename strangeness
        github_variant = variant.replace("N'ER-DO-WELLS", "NER-DO-WELLS") if jset == "J25" else variant
        url = (
            f'https://raw.githubusercontent.com/tyraziel/MTG-JumpStart/main/etc/'
            f'{urllib.parse.quote(jset)}/{urllib.parse.quote(github_variant)}.json'
        )
        try:
            req = requests.get(url, headers=REQUEST_HEADERS, timeout=10)
            if req.status_code == 200:
                data = req.json()
                with open(deck_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f)
                card_count = len(data.get('cards', []))
                print(f"  OK ({card_count} cards)")
                fetched += 1
            else:
                print(f"  FAILED (HTTP {req.status_code})")
                failed += 1
        except Exception as e:
            print(f"  ERROR: {e}")
            failed += 1

    print(f"\nDone. fetched={fetched}  skipped={skipped}  failed={failed}")


def cmd_inspect_cache(args):
    cache_dir = CACHE_TYPE_DIRS.get(args.type)

    if not os.path.exists(cache_dir):
        print(f"Cache directory does not exist: {cache_dir}")
        print("Run 'create-directories' first.")
        return

    files = sorted(os.listdir(cache_dir))
    total_bytes = 0

    if not files:
        print(f"Cache is empty: {cache_dir}/")
        return

    for fname in files:
        fpath = os.path.join(cache_dir, fname)
        size = os.path.getsize(fpath)
        total_bytes += size
        print(f"  {fname:<60}  {size:>10,} bytes")

    total_mb = total_bytes / 1024 / 1024
    print(f"\n{len(files)} files  |  {total_bytes:,} bytes  ({total_mb:.1f} MB)  |  {cache_dir}/")


def cmd_purge_cache(args):
    cache_dir = CACHE_TYPE_DIRS.get(args.type)

    if not os.path.exists(cache_dir):
        print(f"Cache directory does not exist: {cache_dir}")
        return

    files = os.listdir(cache_dir)
    for fname in files:
        os.remove(os.path.join(cache_dir, fname))

    print(f"Purged {len(files)} files from {cache_dir}/")


def cmd_backup_cache(args):
    cache_dir = CACHE_TYPE_DIRS.get(args.type)

    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    backup_path = args.output or os.path.join(BACKUP_DIR, f"cache-{args.type}-{timestamp}.zip")

    if not os.path.exists(cache_dir):
        print(f"Cache directory does not exist: {cache_dir}")
        return

    files = sorted(os.listdir(cache_dir))
    with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for fname in files:
            zf.write(os.path.join(cache_dir, fname), fname)

    size_mb = os.path.getsize(backup_path) / 1024 / 1024
    print(f"Backed up {len(files)} files → {backup_path} ({size_mb:.1f} MB)")


def cmd_import_cache(args):
    cache_dir = CACHE_TYPE_DIRS.get(args.type)
    backup_file = args.backup_file

    if not os.path.exists(backup_file):
        print(f"Backup file not found: {backup_file}")
        sys.exit(1)

    os.makedirs(cache_dir, exist_ok=True)

    imported = skipped = 0
    with zipfile.ZipFile(backup_file, 'r') as zf:
        for name in zf.namelist():
            dest = os.path.join(cache_dir, name)
            if not args.force and os.path.exists(dest):
                skipped += 1
                continue
            zf.extract(name, cache_dir)
            imported += 1

    print(f"Imported {imported} files to {cache_dir}/  ({skipped} skipped; use --force to overwrite)")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        prog='manage_cache.py',
        description='JumpStart Discord Bot — Cache Management',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  python manage_cache.py create-directories
  python manage_cache.py build-cache images
  python manage_cache.py build-cache images --force
  python manage_cache.py build-cache decks
  python manage_cache.py inspect-cache images
  python manage_cache.py inspect-cache scryfall
  python manage_cache.py purge-cache images
  python manage_cache.py backup-cache images
  python manage_cache.py backup-cache decks --output /tmp/decks-backup.zip
  python manage_cache.py import-cache images cache/backups/cache-images-20260613.zip
  python manage_cache.py import-cache images cache/backups/cache-images-20260613.zip --force
        """,
    )

    sub = parser.add_subparsers(dest='command', required=True)

    # create-directories
    sub.add_parser('create-directories', help='Create all cache directories')

    # build-cache
    p = sub.add_parser('build-cache', help='Fetch and store cache entries from upstream APIs')
    p.add_argument('type', choices=['images', 'decks'],
                   help='images = Scryfall card PNGs; decks = GitHub deck list JSONs')
    p.add_argument('--force', action='store_true',
                   help='Re-fetch even if already cached (images also clears Scryfall JSON)')

    # inspect-cache
    p = sub.add_parser('inspect-cache', help='List cache contents and total size')
    p.add_argument('type', choices=['images', 'decks', 'scryfall'])

    # purge-cache
    p = sub.add_parser('purge-cache', help='Delete all files from a cache directory')
    p.add_argument('type', choices=['images', 'decks', 'scryfall'])

    # backup-cache
    p = sub.add_parser('backup-cache', help='Zip a cache directory to a backup file')
    p.add_argument('type', choices=['images', 'decks', 'scryfall'])
    p.add_argument('--output', metavar='PATH', help='Output path (default: cache/backups/)')

    # import-cache
    p = sub.add_parser('import-cache', help='Restore cache from a backup zip file')
    p.add_argument('type', choices=['images', 'decks', 'scryfall'])
    p.add_argument('backup_file', metavar='BACKUP_FILE')
    p.add_argument('--force', action='store_true', help='Overwrite existing cache entries')

    args = parser.parse_args()

    dispatch = {
        'create-directories': cmd_create_directories,
        'build-cache':        cmd_build_cache,
        'inspect-cache':      cmd_inspect_cache,
        'purge-cache':        cmd_purge_cache,
        'backup-cache':       cmd_backup_cache,
        'import-cache':       cmd_import_cache,
    }
    dispatch[args.command](args)


if __name__ == '__main__':
    main()
