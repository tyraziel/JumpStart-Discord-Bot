#!/usr/bin/env python3
"""
Parse J25 (JumpStart 2025) HTML and generate deck list files.

Usage:
    python parse_j25.py < j25_html.txt
    python parse_j25.py j25_html.txt

This script extracts JumpStart deck lists from the official Wizards of the Coast
HTML page for JumpStart 2025 (Foundations) themes.

Output:
    - Creates etc/J25/ directory with all deck list files
    - J25 themes already exist in jumpstartdata.py, this just creates the deck files

Note:
    J25 deck lists have variations indicated by (1), (2), (3), (4) suffixes.
    The script handles these automatically and creates separate files for each variation.

AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0
"""

import re
import os
import sys

# Read HTML from stdin or file
if len(sys.argv) > 1:
    with open(sys.argv[1], 'r') as f:
        html_content = f.read()
else:
    html_content = sys.stdin.read()

# Extract all deck-list blocks
deck_pattern = r'<deck-list[^>]*deck-title="([^"]+)"[^>]*>(.*?)</deck-list>'
main_deck_pattern = r'<main-deck>(.*?)</main-deck>'

decks = re.findall(deck_pattern, html_content, re.DOTALL)

# Get base directory
script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(os.path.dirname(script_dir))  # Go up two levels from etc/parsing-scripts
output_dir = os.path.join(base_dir, 'etc', 'J25')

# Create output directory
os.makedirs(output_dir, exist_ok=True)

# Track unique themes
unique_themes = set()

# Process each deck
deck_count = 0
for deck_title, deck_content in decks:
    # Extract main deck
    main_match = re.search(main_deck_pattern, deck_content, re.DOTALL)
    if not main_match:
        continue

    main_deck = main_match.group(1).strip()

    # Clean up the deck list
    lines = [line.strip() for line in main_deck.split('\n') if line.strip()]

    # Create filename (uppercase, replace spaces with dashes, handle apostrophes and variations)
    # Replace N'er-do-wells with NER-DO-WELLS to match jumpstartdata.py
    filename = deck_title.upper().replace(' ', '-').replace("'", '')

    # Track base theme (without variation numbers)
    base_theme = re.sub(r'-\(\d+\)$', '', deck_title.upper().replace("'", ''))
    unique_themes.add(base_theme)

    # Write deck list file
    filepath = os.path.join(output_dir, f'{filename}.txt')
    with open(filepath, 'w') as f:
        for line in lines:
            f.write(line + '\n')

    deck_count += 1
    print(f"Created: {filepath} - {deck_title}")

print(f"\n\nTotal unique themes: {len(unique_themes)}")
print(f"Total deck files created: {deck_count}")
print("\nNote: J25 themes already exist in jumpstartdata.py (lines 148-193)")
