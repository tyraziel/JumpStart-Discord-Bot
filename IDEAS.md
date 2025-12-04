# JumpStart Discord Bot - Feature Ideas

## Discord Features We Could Use

This document contains ideas for enhancing the JumpStart Discord Bot using various Discord features beyond basic embeds.

---

## 1. Interactive Buttons (discord.ui.Button)

Buttons provide clickable interactions that stay attached to messages.

### Use Cases

**For `!list` command:**
- Navigate between deck variations: `[< Previous] [ANGELS (1)] [Next >]`
- Quick actions: `[📊 Stats] [🎨 Full Art] [🔄 Random Variant]`
- Comparison: `[⚖️ Compare to (2)]`

**For `!pick` command:**
- Reroll: `[🎲 Pick Again]` - reroll with same settings
- Expand: `[📋 Show Lists]` - display full deck lists for all picked themes
- Actions: `[💾 Save] [📤 Share]`

**General:**
- Navigation between related content
- Quick actions without new commands
- Keep context in the same message

### Implementation Notes
- Buttons can persist across bot restarts (with custom_id)
- Max 5 buttons per row, up to 5 rows (25 buttons total)
- Can include emojis and custom labels
- Can be disabled/enabled dynamically

---

## 2. Select Menus/Dropdowns (discord.ui.Select)

Dropdown menus for choosing from multiple options.

### Use Cases

**Set Selection:**
```
Choose Set: [▼ JumpStart 2020]
  ├─ JumpStart 2020
  ├─ JumpStart 2022
  ├─ JumpStart 2025
  ├─ Foundations Beginner Box
  └─ All Sets
```

**Theme Browser:**
```
Browse Themes: [▼ ANGELS]
  ├─ ANGELS (1)
  ├─ ANGELS (2)
  └─ (search/filter options)
```

**Filter Options:**
- Filter by color (W, U, B, R, G, M, N)
- Filter by rarity (M, R, C, U, S)
- Filter by set

### Implementation Notes
- Max 25 options per select menu
- Can have min/max selection counts
- Supports emojis in options
- Can be dynamic based on context

---

## 3. Slash Commands (/)

Modern Discord command format with autocomplete and built-in validation.

### Proposed Commands

```
/pick
  - set: [Dropdown: JMP, J22, J25, etc.]
  - number: [1-10]
  - type: [themes/lists]
  - nodupes: [boolean]

/list
  - theme: [Autocomplete text input]
  - set: [Dropdown: ALL, JMP, J22, etc.]
  - number: [1-4]

/stats
  - (no parameters)

/info
  - (no parameters)

/compare
  - theme1: [text]
  - theme2: [text]
  - set: [optional]
```

### Benefits
- **Autocomplete**: Users can see available options as they type
- **Validation**: Discord validates parameters before sending
- **Discoverability**: Users can browse commands with `/`
- **Better UX**: Modern standard, mobile-friendly
- **Type safety**: Parameters have defined types (string, integer, boolean, etc.)

### Migration Path
1. Keep existing `!` commands for backward compatibility
2. Add slash command equivalents
3. Eventually deprecate `!` commands (with warning period)

---

## 4. Modals (discord.ui.Modal)

Popup forms for collecting structured input.

### Use Cases

**Advanced Search:**
- Multi-field form for complex queries
- Filter by multiple criteria at once
- Save search presets

**Deck Builder:**
- Input multiple themes for custom combinations
- Add notes or preferences

### Implementation Notes
- Up to 5 text input fields per modal
- Triggered by button clicks
- Good for complex input scenarios

---

## 5. Text Formatting Enhancements

### Spoiler Tags
Hide content until user clicks to reveal:
```
Deck List: ||1 Serra Angel\n1 Baneslayer Angel\n...||
```

**Use Cases:**
- Hide deck lists for "blind pick" mode
- Spoiler-free pack reveals
- Tournament mode (hide opponent's picks)

### Code Blocks with Syntax
```md
# Creatures (7)
- 1 Serra Angel
- 1 Baneslayer Angel
...
```

Better formatting for deck lists in some contexts.

### Markdown Links
- Link to Scryfall card pages
- Link to set information
- Link to strategy guides

---

## 6. Reactions

Auto-add emoji reactions for quick interactions.

### Use Cases

**Rating System:**
- ⭐ Favorite this theme
- 👍/👎 Rate the deck
- 🔥 Mark as "spicy"

**Quick Actions:**
- 🎲 React to reroll
- 📋 React to see full list
- 🖼️ React to see all card images

**Bookmarking:**
- 💾 Save this combination
- 📌 Pin for later

### Implementation Notes
- Non-intrusive way to add interactivity
- Works on any message
- Can track who reacted
- Can trigger bot actions based on reactions

---

## 7. Threads

Auto-create discussion threads for picks or lists.

### Use Cases

**Pick Results:**
- Auto-create thread for each pick session
- Players can discuss their combinations
- Share match results
- Keep channel clean (discussions in threads)

**Theme Discussions:**
- Thread per theme for strategy discussion
- Card substitution ideas
- Synergy notes

### Implementation Notes
- Keeps main channel clean
- Organizes related discussions
- Can be auto-archived after inactivity

---

## 8. Ephemeral Messages

Messages only visible to the command user.

### Use Cases

**Error Messages:**
- Show validation errors privately
- Don't clutter public channel

**Personal Stats:**
- Show user's pick history
- Favorite themes
- Personal preferences

**Admin Commands:**
- Cache management responses
- Debug information

---

## Priority Implementation Plan

### Phase 1: Quick Wins (Low effort, high impact)
1. ✅ **Categorized deck lists** using JSON data (in progress)
2. **Variant navigation buttons** for `!list` command
   - `[< Prev] [ANGELS (1)] [Next >]` buttons
3. **"Reroll" button** for `!pick` command

### Phase 2: Enhanced Interactivity (Medium effort)
4. **Deck statistics button** - show CMC, color breakdown, etc.
5. **Spoiler tag option** - hide deck lists until clicked
6. **Select menu for set selection** - better than typing set codes

### Phase 3: Modernization (Higher effort, major improvement)
7. **Migrate to Slash Commands** - modern Discord standard
   - Keep `!` commands for backward compatibility initially
   - Add autocomplete for themes
8. **Persistent buttons** - buttons that work across bot restarts
9. **Thread creation** for pick sessions

### Phase 4: Advanced Features (Nice to have)
10. **Comparison tool** - compare two deck lists side-by-side
11. **User preferences** - save favorite sets, themes
12. **Pick history tracking** - see what you've picked before
13. **Tournament mode** - special features for organized play

---

## Technical Considerations

### Button Persistence
- Use `custom_id` with encoded data (set, theme, variant)
- Max 100 characters in `custom_id`
- Format: `list:JMP:ANGELS:2` or similar

### Rate Limiting
- Buttons don't count toward command rate limits (advantage!)
- But interactions still have limits
- Implement cooldowns if needed

### State Management
- Some features need to track state (user preferences, history)
- Consider adding a simple database (SQLite)
- Or use Discord's built-in user/server settings

### Backward Compatibility
- Keep existing `!` commands working
- Add new features as optional enhancements
- Gradual migration path for users

---

## Community Features (Future)

### Leaderboards
- Most picked themes
- Rarest combinations
- User statistics

### Social Features
- Share pick results
- Challenge friends to use specific themes
- Rate combinations

### Tournament Support
- Swiss pairing helper
- Match reporting
- Standings tracking

---

## Reference Links

- [Discord.py Buttons Documentation](https://discordpy.readthedocs.io/en/stable/interactions/api.html#discord.ui.Button)
- [Discord.py Select Menus](https://discordpy.readthedocs.io/en/stable/interactions/api.html#discord.ui.Select)
- [Discord.py Slash Commands](https://discordpy.readthedocs.io/en/stable/interactions/api.html#discord.app_commands.command)
- [Discord.py Views](https://discordpy.readthedocs.io/en/stable/interactions/api.html#discord.ui.View)

---

**Document Version:** 1.0
**Created:** 2025-12-04
**Last Updated:** 2025-12-04

*Ideas collected during JSON migration planning session*
