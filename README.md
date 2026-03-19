# AI Voice Assistant (Gemini-powered)

Welcome to the smartest voice-activated desktop AI assistant project you’ll meet today. This repository is not just a voice bot; it’s a polished developer lab for automated browser control, advanced webpage analysis, and security-focused code review—fully integrated with Google Gemini 2.5 Flash (Free tier).

---

## 🚀 Why this is exciting

- Real-time voice control: wake up with "Hey assistant" and talk like a human.
- Browser automation: open Wikipedia, search, navigate tabs, scroll, screenshot, and more.
- AI webpage wizard: analyze entire article content, summarize long pages, and extract key points with a single command.
- Code-security engine: detect SQL injection + XSS + code complexity of any project file from VSCode and generate text/output with Gemini intelligence.
- Local-first dev flow: all code is in Python and designed for fast iteration and easy customization.

---

## 💡 Project structure (clean and modular)

- `main.py`, `main_ai.py` - primary bootstrapping + command loop
- `src/core` - app config and logging
- `src/speech` - speech recognition + text-to-speech engines
- `src/browser` - browser controller, navigation, tab management
- `src/ai`:
  - `ai_config.py` (Gemini API settings),
  - `voice_output.py`,
  - `ai_commands.py` (AI orchestration),
  - `analyzers/webpage_analyzer.py`,
  - `analyzers/code_analyzer.py`,
  - `utils/gemini_client.py`
- `tests/` - unit tests for each domain

---

## 🎯 Capabilities

### AI Webpage Analysis (voice-driven)
- "analyze this page" (full AI report)
- "summarize this page" (quick bullet summary)
- "give me key points"

### AI Code Security Analysis
- "analyze code from file" (default analyzes `src/ai/analyzers/test_code.py`)
- "check code clipboard"
- Detects: SQL injection, XSS vulnerabilities
- Complexity metrics via `radon` (average complexity, maintainability index, grade)
- Gemini text analysis and code improvement recommendations

### Browser Control
- `open`, `search`, `open wikipedia <topic>` (smart wiki parser)
- Tab operations, scrolling, screenshots

### Speech Navigation
- Wake/sleep (`hey assistant`, `wake up`, `sleep`)
- Natural phrase mapping (US + UK variants: analyze/analyse, summarize/summarise)

---

## 🛠️ Setup

1. Clone repo
2. Create virtualenv and install dependencies
   ```bash
   conda create --name voice-assistant python=3.10
   conda activate voice-assistant
   pip install -r requirements.txt
   ```
3. Add `.env` file with:
   ```text
   GEMINI_API_KEY=<your-key>
   GEMINI_MODEL=gemini-2.5-flash

   MAX_OUTPUT_TOKENS=2000
   TEMPERATURE=0.7

   ENABLE_AI_FEATURES=true
   ENABLE_WEBPAGE_ANALYSIS=true
   ENABLE_CODE_ANALYSIS=true

   REQUESTS_PER_MINUTE=15
   MONTHLY_TOKEN_LIMIT=1000000
   ```
4. Start the assistant
   ```bash
   python main_ai.py
   ```

---

## 🎙️ Voice UX examples

- "hey assistant" → wakes
- "open wikipedia artificial intelligence" → navigates
- "analyze this page" → page analysis
- "analyze code from file" → security report from `test_code.py`
- "check code clipboard" → analyze clipboard snippet

---

## ✨ Results users get instantly

- Voice responses + console logs that explain what happened
- `Gemini` AI text responses integrated into command flows
- Non-blocking operations with robust error handling
- Easy extension points for new domains (`email`, `jira`, `docs`)

---

## 💬 Want to extend?

- add new analyzer in `src/ai/analyzers/<your-analyzer>.py`
- register intent in `src/commands/command_parser.py`
- plug into `src/ai/ai_commands.py`

---

## 🧪 Tests

Run:
```bash
pytest -q
```

---

## 🙌 Final takeaway
This project is designed to wow the first user and stay practical for the 100th iteration. It’s the perfect demo stack for AI voice integration with practical security workflows — and it’s built to keep the audience engaged, not bored.