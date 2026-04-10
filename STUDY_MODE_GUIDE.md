# Study Mode - User Guide & Documentation

## Quick Start

Say any of these voice commands to launch Study Mode:
- **"study mode"** — Launch with default topic
- **"study mode React"** — Study React
- **"start studying Python machine learning"** — Study Python ML
- **"focus mode web development"** — Study web dev
- **"learning mode data structures"** — Study data structures

## What Study Mode Does

When you trigger Study Mode, the voice assistant automatically:

1. **🔕 Mutes Notifications** — Enables Windows Focus Assist to minimize distractions
2. **📺 Opens YouTube** — Searches for your topic (or default) for tutorial videos
3. **📚 Opens Documentation** — GeeksforGeeks or your configured docs site
4. **📝 Opens Notepad** — Ready for you to take notes

All of this happens in **seconds**, preparing you for a focused study session.

## Voice Command Formats

### With a Topic (Recommended)
```
"study mode [topic]"
"start studying [topic]"
"focus mode [topic]"
"learning mode [topic]"
"begin studying [topic]"
"study session [topic]"
```

**Examples:**
- "study mode Python dictionaries"
- "start studying React hooks and context"
- "focus mode machine learning algorithms"
- "learning mode database design"

### Without a Topic
```
"study mode"
"start studying"
"focus mode"
```

Falls back to default topic configured in `config.json` (default: "programming tutorial")

## Configuration

Edit `config.json` at the project root to customize Study Mode:

```json
{
  "study_mode": {
    "youtube_url": "https://www.youtube.com/results?search_query={topic}",
    "docs_url": "https://www.geeksforgeeks.org",
    "notepad_command": "notepad.exe",
    "mute_notifications_command": "focus_assist_on",
    "default_topic": "programming tutorial"
  }
}
```

### Configuration Options

| Setting | Default | Purpose |
|---------|---------|---------|
| `youtube_url` | YouTube search template | URL to search for videos (keep `{topic}` placeholder) |
| `docs_url` | GeeksforGeeks | Documentation reference site |
| `notepad_command` | `notepad.exe` | Text editor for notes (can use VSCode, etc.) |
| `mute_notifications_command` | `focus_assist_on` | Command to suppress notifications |
| `default_topic` | `"programming tutorial"` | Fallback topic if none provided |

### Customization Examples

**Use Visual Studio Code for Notes:**
```json
"notepad_command": "code"  // Opens VS Code instead of Notepad
```

**Change Documentation Site:**
```json
"docs_url": "https://developer.mozilla.org"  // MDN instead of GeeksforGeeks
```

**Use W3Schools as Default Docs:**
```json
"docs_url": "https://www.w3schools.com"
```

**Set a Custom Default Topic:**
```json
"default_topic": "competitive programming"
```

## How Topics Work

### Topic Extraction
Everything you say **after** the keyword becomes your topic:

```
Command: "study mode react hooks and context"
Keyword: "study mode"
Topic: "react hooks and context"
Result: YouTube searches for "react hooks and context"
```

### Multi-Word Topics
Topics with multiple words are fully supported:

```
"study mode web development best practices"
    → YouTube searches for: "web development best practices"

"start studying machine learning for beginners"
    → YouTube searches for: "machine learning for beginners"

"focus mode advanced JavaScript async await"
    → YouTube searches for: "advanced JavaScript async await"
```

### Default Topic
If you don't specify a topic:

```
"study mode"
    → Uses default from config: "programming tutorial"
    → YouTube searches for: "programming tutorial"
```

## Behind the Scenes: How It Works

### 1. Voice Input
```
User says: "study mode React"
```

### 2. Command Parsing
```python
# Parser detects keyword "study mode"
# Extracts topic "React"
# Returns: {'intent': 'start_study', 'params': {'topic': 'React'}}
```

### 3. URL Construction
```python
# Template: "https://www.youtube.com/results?search_query={topic}"
# Topic: "React"
# Final URL: "https://www.youtube.com/results?search_query=React"
```

### 4. Sequential Execution
```
Step 1: Run mute_notifications_command
  ↓
Step 2: Open YouTube URL in browser
  ↓
Step 3: Open docs_url in new tab
  ↓
Step 4: Launch notepad_command
  ↓
✅ Study Mode Ready!
```

### 5. Voice Feedback
```
"Study mode is ready. YouTube, documentation, and notepad have 
been opened. Good luck studying!"
```

## Common Use Cases

### Case 1: Quick Tutorial Search
```
You: "study mode Python list comprehensions"
➜ YouTube opens with Python list comprehension tutorials
➜ Docs open for reference
➜ Notepad ready for notes
```

### Case 2: Long Study Session
```
You: "start studying advanced algorithms"
➜ Notifications muted (no distractions!)
➜ YouTube for videos
➜ GeeksforGeeks for algorithms reference
➜ Notepad for pseudocode/notes
```

### Case 3: Language Learning
```
You: "focus mode Russian grammar"
➜ YouTube with Russian grammar tutorials
➜ Reference docs
➜ Notepad for conjugation notes
```

## Troubleshooting

### Issue: "Study mode starts but browser doesn't open"
**Solution:** Check your internet connection. The `webbrowser` module requires connectivity.

### Issue: "Notepad doesn't launch"
**Solution:** Verify `notepad_command` in config.json. Try:
- `"notepad.exe"` (Windows built-in)
- `"code"` (VS Code)
- `"nvim"` (Neovim)

### Issue: "Notifications not muting"
**Solution:** Muting requires admin rights on Windows. Try:
- Run voice assistant as Administrator
- Or leave `mute_notifications_command` empty in config to skip

### Issue: "Custom docs URL not opening"
**Solution:** 
1. Check URL is valid (starts with `https://`)
2. Verify internet connection
3. Try a different URL to test

### Issue: "YouTube URL showing weird characters"
**Solution:** This is normal! Topics like "C++" are URL-encoded:
- `C++` → `C%2B%2B` (proper encoding)
- Still works correctly once loaded

## Advanced Topics

### Changing Focus Assist Behavior

The default `focus_assist_on` enables Windows Focus Assist:
- **0** = Off (notifications visible)
- **1** = Priority only (only important notifications)
- **2** = Alarms only (max focus mode)

Registry command to change:
```powershell
Set-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Notifications\Settings' `
-Name 'NOC_GLOBAL_SETTING_TOASTS_ENABLED' -Value 0 -Type DWord -Force
```

### Using Custom Topic Base URL

If you want YouTube search to use a different approach:
```json
"youtube_url": "https://www.youtube.com/search?q={topic}"
```

### Disabling Features You Don't Want

To skip opening YouTube (docs only):
```json
"youtube_url": ""  // Empty string disables this step
```

To skip opening docs:
```json
"docs_url": ""  // Empty string disables this step
```

To skip opening notepad:
```json
"notepad_command": ""  // Empty string disables this step
```

## Integration with Voice Assistant

Study Mode is integrated with the main voice assistant flow:

1. **Priority** — Checked AFTER AI/Coding commands, BEFORE YouTube/Navigation
2. **Intent** — Named `'start_study'` in the command router
3. **Handler** — `_handle_start_study()` in `main.py`
4. **Parser** — Study mode keywords detected in `CommandParser`

To see all available commands (including Study Mode):
```
User: "help"
```

Also shows Study Mode in the command menu with examples.

## Testing

Run the test suite:
```bash
python test_study_mode.py --test all
```

Simulate a command:
```bash
python test_study_mode.py --simulate "study mode python lists"
```

## Summary

Study Mode is designed to **minimize friction** when you want to start learning:

✅ Single voice command  
✅ Automatic browser + docs + notes setup  
✅ Notifications muted for focus  
✅ Fully configurable  
✅ Multi-word topic support  
✅ Fallback to default topic  
✅ Integrated with existing voice commands  

Start studying: **"study mode [what you want to learn]"**
