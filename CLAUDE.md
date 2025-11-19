# JumpStart Discord Bot - Project Status

**Version:** v1.0.5-ga
**Language:** Python 3.x
**License:** MIT
**Last Major Update:** See git commit 0a9bdeb

---

## Project Overview

A Discord bot for Magic: The Gathering JumpStart format that helps users:
- Pick random JumpStart packs/themes from various sets
- Look up specific deck lists
- View card images and set information
- Simulate the JumpStart pack opening experience

### Supported Sets
- **JMP** - JumpStart 2020
- **J22** - JumpStart 2022
- **J25** - JumpStart 2025
- **FDN** - JumpStart 2025 Beginner Box (partial - only 2/10 themes active)
- **DMU** - Dominaria United JumpStart
- **BRO** - The Brother's War JumpStart
- **ONE** - Phyrexia: All Will Be One JumpStart
- **MOM** - March of the Machine JumpStart
- **LTR** - Lord of the Rings: Tales of Middle-earth JumpStart
- **CLU** - Ravnica: Clue Edition

---

## Architecture

### Core Files

#### `bot.py` (Main Application)
- **Line 31:** Version tracking (`v1.0.5-ga`)
- Discord.py 2.3.2 bot implementation
- Command prefix: `!`
- Supports DEV and PROD environments via CLI arguments
- Implements rate limiting for Scryfall API (100ms sleep between requests)

**Commands:**
- `!pick` / `!p3` / `!mtga` - Pick random packs (default: 3)
- `!list` - Look up specific deck list
- `!stats` - View cache statistics
- `!info` - Bot and license information
- `!buildPickCache` / `!bPC` - (Owner only) Pre-cache all theme images
- `!purgeListCache` / `!pLC` - (Owner only) Clear list cache
- `!purgeImageCache` / `!pIC` - (Owner only) Clear image cache
- `!purgeScryfallCache` / `!pSC` - (Owner only) Clear Scryfall JSON cache

**Features:**
- Auto-fixes fancy Unicode quotes and dashes (lines 133-141)
- Test mode: Only responds in `#bot-testing` channel when `-t` flag set
- Logging to both console and file (`bot-log.log`)
- Discord presence: "Listening to JumpStart Lo-Fi"

#### `bot_cache.py` (Caching System)
Three-tier caching system:
1. **uniqueListCache** - GitHub deck lists
2. **scryFallJSONCardCache** - Scryfall card JSON data
3. **imageCache** - Card images (PIL Image objects)

Fetches from:
- GitHub: `https://raw.githubusercontent.com/tyraziel/MTG-JumpStart/main/etc/{SET}/{THEME}.txt`
- Scryfall API: `https://api.scryfall.com/cards/named?exact={THEME}&set={SET_CODE}`

**Special Handling:**
- `BRO/UNEARTH` → `UNEARTH-(THEME)` (line 71-72)
- `J22/BLINK` → `BLINK-(FRONT-CARD)` (line 73-74)
- `J25/N'ER-DO-WELLS` → `NEER-DO-WELLS` (line 75-76)

#### `jumpstartdata.py` (Data Store)
- **195 total themes** across all sets
- Rarity tiers: M (Mythic), R (Rare), S (Special), C (Common), U (Uncommon)
- Color coding: W, U, B, R, G, M (Multicolor), N (Neutral/Colorless)
- Set metadata with Scryfall codes and icon URLs

---

## Current State

### Recent Changes (Git History)
```
0a9bdeb - Fixed logging messup. Incremented Version. Fixed set information. Fixed Caching.
51e3ec2 - Merge branch 'main'
0ab4200 - Added Purging (cache management commands)
53b6646 - Updated Arguments
9a3d86e - Added Foundations Beginner Box Themes
```

### Active Development Branch
- **Branch:** `claude/review-documents-01RQubwKRyxqGYmgBgLcRD45`
- **Status:** Clean working tree

### Dependencies (requirements.txt)
```
discord.py==2.3.2         ✓ Current
python-dotenv==1.0.0      ✓ Current
argparse==1.4.0           ⚠ Built-in to Python 3.2+, unnecessary dependency
requests==2.31.0          ✓ Current
pillow==10.1.0            ⚠ Check for security updates (released Oct 2023)
```

---

## Known Issues & Considerations

### 1. FDN Set Incomplete
**Location:** `jumpstartdata.py:195-204`
- Only 2 of 10 themes are active (CATS, VAMPIRES)
- 8 themes commented out:
  - HEALING (W), WIZARDS (U), PIRATES (U)
  - UNDEAD (B), GOBLINS (R), INFERNO (R)
  - ELVES (G), PRIMAL (G)

**Impact:** Users cannot pick or list these themes

### 2. Deprecated Dependency
**Location:** `requirements.txt:3`
- `argparse==1.4.0` is unnecessary (built into Python 3.2+)
- Can be safely removed

### 3. Security Considerations
- **Pillow 10.1.0** released October 2023 - check for CVE updates
- **requests 2.31.0** - should verify latest version
- Environment files (`.devenv`, `.prodenv`) contain bot tokens - properly gitignored

### 4. Code Quality Notes
- Some commented-out code in `bot.py` (lines 145-220) - consider cleanup
- `BotCache.__init__` has unused variable `theVariable` (bot_cache.py:26)
- Inconsistent error handling in some fetch methods
- No type hints (Python 3.5+ feature)

### 5. Scryfall API Rate Limiting
- Current: 100ms sleep between requests (line 101, 174)
- Scryfall allows 10 requests/second
- Consider implementing exponential backoff for errors

### 6. Duplicate Function Name
**Location:** `bot.py:192`
- Two functions named `purgeImageCache` (lines 182 and 192)
- Second one should likely be different or was copy-paste error

---

## Potential Updates & Improvements

### High Priority

#### 1. Complete FDN Set
**Effort:** Low | **Impact:** High
- Uncomment remaining 8 FDN themes in `jumpstartdata.py`
- Verify Scryfall card names match
- Test image fetching for all themes

#### 2. Fix Duplicate Function Name
**Effort:** Minimal | **Impact:** Medium
- Review `purgeImageCache` functions at lines 182 and 192
- Rename or remove duplicate

#### 3. Update Dependencies
**Effort:** Low | **Impact:** Medium (Security)
```bash
# Check for updates
pip list --outdated

# Particularly check:
- pillow (security patches)
- requests (security patches)
- discord.py (new features/fixes)
```

#### 4. Remove argparse Dependency
**Effort:** Minimal | **Impact:** Low
- Remove line 3 from `requirements.txt`
- argparse is built-in to Python 3.2+

### Medium Priority

#### 5. Add Type Hints
**Effort:** Medium | **Impact:** Medium (Code Quality)
- Add type annotations to function signatures
- Improves IDE support and catches bugs early

#### 6. Improve Error Handling
**Effort:** Medium | **Impact:** Medium
- Add try-except blocks around API calls
- Implement retry logic with exponential backoff
- Better user-facing error messages

#### 7. Add Unit Tests
**Effort:** High | **Impact:** High (Long-term)
- Test cache mechanisms
- Test command parsing
- Test Scryfall API integration (with mocks)

#### 8. Configuration Management
**Effort:** Medium | **Impact:** Medium
- Move hardcoded URLs to config
- Centralize retry logic and timeouts
- Consider using `config.py` or `settings.py`

### Low Priority

#### 9. Code Cleanup
**Effort:** Low | **Impact:** Low
- Remove commented-out code
- Remove unused variables (`theVariable` in BotCache.__init__)
- Consistent naming conventions

#### 10. Documentation
**Effort:** Medium | **Impact:** Medium
- Add docstrings to all functions
- Create user guide for commands
- Document development setup process

#### 11. Metrics & Monitoring
**Effort:** Medium | **Impact:** Low
- Enhanced logging for production
- Discord webhooks for error alerts
- Track command usage statistics

#### 12. Feature Enhancements
**Effort:** Varies | **Impact:** Medium-High
- Add `--random` flag to pick random set
- Support for "sealed" mode (pick 2 packs automatically)
- Favorite themes per user
- Theme statistics (most picked, etc.)
- Slash commands (Discord's new command system)

---

## Development Setup

### Environment Files Required
Create two files (these are gitignored):
- `.devenv` - Development bot token
- `.prodenv` - Production bot token

Format:
```
BOT_TOKEN=your_discord_bot_token_here
```

### Running the Bot

**Development Mode:**
```bash
python bot.py -e DEV
```

**Production Mode:**
```bash
python bot.py -e PROD
```

**With Pre-caching:**
```bash
python bot.py -e DEV --loadcache
```

**Test Mode (bot-testing channel only):**
```bash
python bot.py -e DEV --test
```

**Debug Logging:**
```bash
python bot.py -e DEV --debug
```

### Installation
```bash
pip install -r requirements.txt
```

---

## External Dependencies

### APIs
1. **Scryfall API** - https://api.scryfall.com/
   - Card data and images
   - Rate limit: 10 req/sec (we use 10 req/sec with 100ms sleep)
   - No API key required

2. **GitHub Raw Content** - https://raw.githubusercontent.com/
   - Deck lists from tyraziel/MTG-JumpStart repository
   - No rate limits for public repos

### Image Sources
- Scryfall card images: `https://cards.scryfall.io/`
- Set icons: `https://static.wikia.nocookie.net/mtgsalvation_gamepedia/`

---

## Fan Content Notice

This bot is unofficial Fan Content permitted under the Wizards of the Coast Fan Content Policy.
- Not approved/endorsed by Wizards of the Coast
- Materials used are property of Wizards of the Coast
- ©Wizards of the Coast LLC
- https://company.wizards.com/en/legal/fancontentpolicy

Pack distributions are based on observation, guesswork, testing, and validation.

---

## AI Development Guidelines

*AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0*

This section provides technical guidelines for AI-assisted development on the JumpStart Discord Bot project. All AI assistants (Claude, Copilot, etc.) should follow these practices to maintain code quality, test coverage, and proper attribution.

### AI Attribution (AIA) Requirements

#### Mandatory Attribution

All AI-generated or AI-assisted code MUST include proper attribution following the **AIA (AI Attribution) standard**.

#### Attribution Format

**JumpStart Discord Bot uses the following AIA attribution format:**

**Short Form (for file headers and inline comments):**
```
AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0
```

Where:
- **AIA** = AI Attribution
- **EAI** = Entirely AI-generated
- **Hin** = Human-initiated
- **R** = Reviewed (by human)
- **Claude Code [Sonnet 4.5]** = The AI model/tool used
- **v1.0** = Version number

**Long Form (for documentation and detailed attribution):**
```
AIA Entirely AI, Human-initiated, Reviewed, Claude Code [Sonnet 4.5] v1.0

This work was entirely AI-generated. AI was prompted for its contributions, or
AI assistance was enabled. AI-generated content was reviewed and approved. The
following model(s) or application(s) were used: Claude Code [Sonnet 4.5].
```

**Official AIA Statement:**
https://aiattribution.github.io/statements/AIA-EAI-Hin-R-?model=Claude%20Code%20%5BSonnet%204.5%5D-v1.0

#### Using Different AI Models

The examples in this document use **Claude Code [Sonnet 4.5]** as the primary AI assistant. If using a different AI model or tool, adjust the attribution accordingly:

**Claude Model Variants:**
- **Claude Sonnet 4.5** (current): `Claude Code [Sonnet 4.5]`
- **Claude Opus 4**: `Claude Code [Opus 4]`
- **Claude Haiku 4**: `Claude Code [Haiku 4]`

**Other AI Tools:**
- **GitHub Copilot**: `GitHub Copilot`
- **Cursor AI**: `Cursor AI`
- **Custom AI assistants**: Use the appropriate model name and version

**Co-authorship Examples:**

For Claude Opus:
```
Co-authored-by: Claude Code [Opus 4] <claude@anthropic.com>
```

For GitHub Copilot:
```
Co-authored-by: GitHub Copilot <copilot@github.com>
```

For Cursor AI:
```
Co-authored-by: Cursor AI <ai@cursor.sh>
```

**Important:** AI models should self-identify in their commit messages with accurate model information. Always verify the attribution matches the actual AI tool being used.

#### File Headers

Every new file created with AI assistance must include:

```python
"""
Module description here.

AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0
"""
```

**Example:**
```python
"""
Tournament pairing algorithms for Swiss-system tournaments.

AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0
"""
```

For files with multiple AI contributions over time:
```python
"""
Tournament pairing algorithms for Swiss-system tournaments.

AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0 - 2025-01-15 - Initial implementation
AIA PAI Hin R Claude Code [Sonnet 4.5] v1.0 - 2025-01-16 - Refactored for async (Partial AI)
"""
```

#### Significant Code Changes

For substantial modifications (>50 lines or core logic changes), add inline attribution:

```python
# AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0
def calculate_omw_percentage(player: Player, rounds: list[Round]) -> float:
    """Calculate Opponent Match Win Percentage for tiebreaker."""
    # Implementation here
```

Or with date and description for clarity:
```python
# AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0 - 2025-01-15 - OMW% tiebreaker implementation
def calculate_omw_percentage(player: Player, rounds: list[Round]) -> float:
    """Calculate Opponent Match Win Percentage for tiebreaker."""
    # Implementation here
```

#### Commit Messages

All commits with AI assistance must include attribution and co-authorship in the commit message:

**Short form (standard commits):**
```bash
git commit -m "Add Swiss pairing algorithm

- Implemented first round random pairing
- Added OMW% tiebreaker calculation
- Test coverage: 92%

AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0

Vibe-Coder: Andrew Potozniak <vibecoder.1.z3r0@gmail.com>
Co-authored-by: Claude Code [Sonnet 4.5] <claude@anthropic.com>"
```

**Long form (detailed commits with full attribution):**
```bash
git commit -m "Add Swiss pairing algorithm

Implemented Swiss-system pairing algorithm with proper tiebreakers.

Features:
- First round random pairing
- Subsequent rounds paired by standings
- OMW%/GW%/OGW% tiebreaker support
- Comprehensive test coverage

AIA Entirely AI, Human-initiated, Reviewed, Claude Code [Sonnet 4.5] v1.0

This work was entirely AI-generated. AI was prompted for its contributions, or
AI assistance was enabled. AI-generated content was reviewed and approved. The
following model(s) or application(s) were used: Claude Code [Sonnet 4.5].

Vibe-Coder: Andrew Potozniak <vibecoder.1.z3r0@gmail.com>
Co-authored-by: Claude Code [Sonnet 4.5] <claude@anthropic.com>"
```

**Required commit trailer lines:**
- `Vibe-Coder: Andrew Potozniak <vibecoder.1.z3r0@gmail.com>` - Project lead attribution
- `Co-authored-by: Claude Code [Sonnet 4.5] <claude@anthropic.com>` - AI co-authorship

#### Session Tracking

Update session tracking documentation (if maintained) with:
- Date and duration
- AI model and version
- Features/changes implemented
- Test coverage added
- Issues encountered and resolved

---

## Next Steps Recommendation

### ✓ Completed (2025-11-19)
1. **Immediate fixes:**
   - ✓ Fixed duplicate function name (purgeListCache)
   - ✓ Removed argparse from requirements.txt
   - ✓ Updated all dependencies (Pillow 12.0.0, discord.py 2.6.4, requests 2.32.5, python-dotenv 1.2.1)
   - ✓ Completed FDN set (all 10 themes enabled)
   - ✓ Added AI Development Guidelines to CLAUDE.md

### Upcoming Priorities

1. **Short-term (1-2 weeks):**
   - Add basic error handling improvements
   - Clean up commented code (bot.py lines 145-220)
   - Remove unused variables

3. **Medium-term (1-2 months):**
   - Add type hints
   - Implement comprehensive testing
   - Consider slash commands migration

4. **Long-term:**
   - Enhanced features (user preferences, statistics)
   - Monitoring and analytics
   - Performance optimization

---

**Document Version:** 1.1
**Created:** 2025-11-18
**Last Updated:** 2025-11-19

*AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0*
