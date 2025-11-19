#!/usr/bin/env python3
"""
Parse TLA (Avatar: The Last Airbender) HTML and generate deck list files.

Usage:
    python parse_tla.py < tla_html.txt

This script extracts JumpStart deck lists from the official Wizards of the Coast
HTML page for Avatar: The Last Airbender JumpStart themes.

Output:
    - Creates etc/TLA/ directory with all deck list files
    - Generates 66 deck files (46 themes with variations)
    - Prints summary of themes for jumpstartdata.py

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

# Color mapping based on HTML sections
color_map = {
    'Aang': 'W', 'Swordmaster': 'W', 'Airbending': 'W', 'Freedom Fighters': 'W', 'Warriors': 'W',
    'Hei Bai (1)': 'W', 'Hei Bai (2)': 'W', 'Gliding (1)': 'W', 'Gliding (2)': 'W',
    'Insurgent (1)': 'W', 'Insurgent (2)': 'W', 'Alliance (1)': 'W', 'Alliance (2)': 'W',

    'Katara': 'U', 'Librarian': 'U', 'Spirit': 'U', 'Underwater': 'U', 'Adaptive': 'U',
    'Wise (1)': 'U', 'Wise (2)': 'U', 'Soaring (1)': 'U', 'Soaring (2)': 'U',
    'Adept (1)': 'U', 'Adept (2)': 'U', 'Lessons (1)': 'U', 'Lessons (2)': 'U',

    'Azula': 'B', 'Ozai': 'B', 'Nightmares': 'B', 'Bad Advice': 'B', 'Siege Engines': 'B',
    'Bounty Hunter (1)': 'B', 'Bounty Hunter (2)': 'B', 'Relentless (1)': 'B', 'Relentless (2)': 'B',
    'Reinforced (1)': 'B', 'Reinforced (2)': 'B', 'Hunting (1)': 'B', 'Hunting (2)': 'B',

    'Zuko': 'R', 'Roku': 'R', 'Iroh': 'R', 'Fire Nation': 'R', 'Musicians': 'R',
    'Rebelling (1)': 'R', 'Rebelling (2)': 'R', 'Firebending (1)': 'R', 'Firebending (2)': 'R',
    'Sparky Sparky (1)': 'R', 'Sparky Sparky (2)': 'R', 'Powerful (1)': 'R', 'Powerful (2)': 'R',

    'Toph': 'G', 'Kyoshi': 'G', 'At the Zoo': 'G', 'Cabbages': 'G', 'Bumi': 'G',
    'Earth Rumble (1)': 'G', 'Earth Rumble (2)': 'G', 'Earth Kingdom (1)': 'G', 'Earth Kingdom (2)': 'G',
    'Learning (1)': 'G', 'Learning (2)': 'G', 'Earthbending (1)': 'G', 'Earthbending (2)': 'G',

    'Shrines': 'M'
}

# Rarity mapping (M for single variation, R for double variation)
rarity_map = {}
# Mythics (single variation)
mythics = ['Aang', 'Swordmaster', 'Airbending', 'Freedom Fighters', 'Warriors',
           'Katara', 'Librarian', 'Spirit', 'Underwater', 'Adaptive',
           'Azula', 'Ozai', 'Nightmares', 'Bad Advice', 'Siege Engines',
           'Zuko', 'Roku', 'Iroh', 'Fire Nation', 'Musicians',
           'Toph', 'Kyoshi', 'At the Zoo', 'Cabbages', 'Bumi',
           'Shrines']
for m in mythics:
    rarity_map[m] = 'M'

# Rares (double variation) - themes with (1) and (2)
rares_base = ['Hei Bai', 'Gliding', 'Insurgent', 'Alliance',
              'Wise', 'Soaring', 'Adept', 'Lessons',
              'Bounty Hunter', 'Relentless', 'Reinforced', 'Hunting',
              'Rebelling', 'Firebending', 'Sparky Sparky', 'Powerful',
              'Earth Rumble', 'Earth Kingdom', 'Learning', 'Earthbending']
for r in rares_base:
    rarity_map[f'{r} (1)'] = 'R'
    rarity_map[f'{r} (2)'] = 'R'

# Get base directory
script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(os.path.dirname(script_dir))  # Go up two levels from etc/parsing-scripts
output_dir = os.path.join(base_dir, 'etc', 'TLA')

# Create output directory
os.makedirs(output_dir, exist_ok=True)

# Process each deck
themes_data = []
for deck_title, deck_content in decks:
    # Extract main deck
    main_match = re.search(main_deck_pattern, deck_content, re.DOTALL)
    if not main_match:
        continue

    main_deck = main_match.group(1).strip()

    # Clean up the deck list
    lines = [line.strip() for line in main_deck.split('\n') if line.strip()]

    # Get color and rarity
    color = color_map.get(deck_title, 'N')
    rarity = rarity_map.get(deck_title, 'M')

    # Create filename (uppercase, replace spaces with dashes, handle (1)/(2))
    filename = deck_title.upper().replace(' ', '-').replace('(', '').replace(')', '')
    if filename.endswith('-1'):
        filename = filename[:-2] + '-1'
    elif filename.endswith('-2'):
        filename = filename[:-2] + '-2'

    # Write deck list file
    filepath = os.path.join(output_dir, f'{filename}.txt')
    with open(filepath, 'w') as f:
        for line in lines:
            f.write(line + '\n')

    # Store theme data (only base theme names without (1)/(2) for jumpstartdata.py)
    base_theme = deck_title.replace(' (1)', '').replace(' (2)', '').upper()
    if base_theme not in [t['theme'] for t in themes_data]:
        themes_data.append({
            'theme': base_theme,
            'rarity': rarity,
            'color': color
        })

    print(f"Created: {filepath} - {deck_title} ({color}, {rarity})")

# Print themes_data for jumpstartdata.py
print("\n\nThemes for jumpstartdata.py:")
print("="*60)
for theme in themes_data:
    theme_name = theme["theme"]
    rarity = theme["rarity"]
    color = theme["color"]
    print(f'    {{"Set": "TLA", "Theme" : "{theme_name}", "Rarity": "{rarity}", "PrimaryColor": "{color}"}},')

print(f"\n\nTotal themes: {len(themes_data)}")
print(f"Total deck files: {len(decks)}")
