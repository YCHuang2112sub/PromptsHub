#  PromptsHub: AlphaMind Edition (v3.0)

> **Codename**: AlphaMind | **Vision**: Alicization | **Status**: Active Symbiosis

PromptsHub is a high-performance workspace for AI-human collaboration. It transforms your desktop into an intelligent environment that captures, processes, and reverse-engineers text and vision in real-time.

---

##  Key Capabilities

###  Live Capture & Vision
- **Smart Clipboard**: Automatically captures text copies for instant AI refinement.
- **Side-by-Side Editor**: Real-time comparison view showing original input vs. AI-processed output.
- **Screen OCR**: Extract text from any screen area using Gemini Vision APIs.
- **Vision Chat**: Upload images or screenshots and ask the AI complex questions about them.
- **Smart Region Monitor**: 
  - Place a floating window over any area (e.g., a code editor, a chat, or a video).
  - The system auto-detects changes and triggers OCR/Analysis instantly.
- **Privacy Mode (Default-ON)**: Prevents the application window from being captured in its own screenshots/recordings.

###  Intelligence Suite
- **Multi-Provider Support**: Seamless switching between **Gemini 2.5 Flash**, **GPT-4**, and **Claude 3**.
- ** Extract Prompt**: Reverse-engineer any text output into a reusable prompt template with `["Input"]` placeholders.
- **"Enchant"**: Instantly polish, professionalize, or transform text using pre-built AI templates.
- **Audio Intelligence**: Real-time system audio transcription directly into your workspace.

###  Prompt Library & Management
- **Foldable Sidebar**: Always-accessible prompt library for side-by-side editing and template application.
- **Dynamic Categories**: Organize your prompts with icons and custom groups.
- **Smart History**: Persistent storage of every capture with searchable snippets.

---

##  Getting Started

### Prerequisites
```bash
# Core dependencies
python -m pip install customtkinter pillow requests pyperclip python-dotenv sounddevice numpy SpeechRecognition
```

### Configuration
1. Clone the repository.
2. Copy `.env.template` to `.env.local`.
3. Add your API keys:
   ```env
   GOOGLE_API_KEY=AIza...
   OPENAI_API_KEY=sk-...
   ANTHROPIC_API_KEY=sk-ant-...
   ```

### Usage
Run with Administrator privileges (recommended for global hotkeys and monitoring):
```powershell
python prompts_hub.py
```

---

##  Privacy & Security
- **Privacy Mode is enabled by default** on Windows. This uses `WDA_EXCLUDEFROMCAPTURE` to ensure your PromptsHub workspace stays private during screen shares or OCR captures.
- **Local Database**: All library and history data is stored locally in `prompts_hub.db`.

---

##  License & Acknowledgments

Apache License 2.0 - See [LICENSE](file:///c:/Users/User/Downloads/workspace/PromptsHub/LICENSE) and [NOTICE](file:///c:/Users/User/Downloads/workspace/PromptsHub/NOTICE) for details.

Developed with by Yu-Cheng Huang.
