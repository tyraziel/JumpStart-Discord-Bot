# JumpStart Deck List Parsing Scripts

This directory contains Python scripts for parsing official Wizards of the Coast HTML pages to extract JumpStart deck lists.

## Scripts

### `parse_tla.py` - Avatar: The Last Airbender
Parses TLA (Avatar: The Last Airbender) JumpStart deck lists.

**Usage:**
```bash
python parse_tla.py < tla_html.txt
# or
python parse_tla.py tla_html.txt
```

**Output:**
- Creates `etc/TLA/` directory with 66 deck list files
- 46 unique themes (26 Mythic, 20 Rare with variations)
- Prints theme data ready for `jumpstartdata.py`

**Theme Structure:**
- **Mythic (M)**: Single variation themes (5 per color + 1 multicolor)
- **Rare (R)**: Double variation themes (4 per color, with -1 and -2 suffixes)

### `parse_j25.py` - JumpStart 2025 (Foundations)
Parses J25 (JumpStart 2025) deck lists from the Foundations release.

**Usage:**
```bash
python parse_j25.py < j25_html.txt
# or
python parse_j25.py j25_html.txt
```

**Output:**
- Creates `etc/J25/` directory with all deck list files
- Handles variations (1), (2), (3), (4) automatically
- J25 themes already exist in `jumpstartdata.py` (lines 148-193)

## Getting HTML Content

To use these scripts, you need to get the HTML from the official Wizards pages:

### For TLA:
1. Visit: https://magic.wizards.com/en/news/announcements/avatar-the-last-airbender-jumpstart-booster-themes
2. View page source (Ctrl+U or Cmd+Option+U)
3. Copy all `<deck-list>` sections
4. Save to `tla_html.txt`

### For J25:
1. Visit: https://magic.wizards.com/en/news/announcements/jumpstart-2025-booster-themes
2. View page source
3. Copy all `<deck-list>` sections
4. Save to `j25_html.txt`

## File Naming Conventions

The scripts automatically convert theme names to filename format:
- Uppercase all letters
- Replace spaces with dashes
- Remove apostrophes
- Keep variation numbers: `(1)` → `-1`, `(2)` → `-2`, etc.

**Examples:**
- "N'er-do-wells (1)" → `NER-DO-WELLS-1.txt`
- "At the Zoo" → `AT-THE-ZOO.txt`
- "Hei Bai (1)" → `HEI-BAI-1.txt`

## Output Format

Deck list files contain one card per line:
```
Momo, Rambunctious Rascal
Kindly Customer
Invasion Reinforcements
7 Plains
...
```

Card names with quantities and set codes are preserved as-is from the HTML.

## Integration with jumpstartdata.py

After running the parsers:
1. The deck files are created in `etc/{SET}/` directories
2. For TLA: Copy the printed theme data into `jumpstartdata.py`
3. For J25: Themes already exist, no changes needed to `jumpstartdata.py`

## Requirements

- Python 3.6+
- No external dependencies (uses only stdlib: `re`, `os`, `sys`)

## Attribution

AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0

These scripts were created with AI assistance to help manage JumpStart Discord Bot deck lists.
