[![☕ Buy me a coffee](https://img.shields.io/badge/☕-Buy%20me%20a%20coffee-orange.svg?style=for-the-badge&logo=buy-me-a-coffee)](https://buymeacoffee.com/yuchenghuang)

# 📋 PromptsHub

> **Codename**: AlphaMind | **Vision**: Alicization  

A clean, minimal tool for clipboard monitoring, screen OCR, and LLM text processing.

## ✨ AlphaMind Edition Features

### 🎯 Live Capture & Vision
- **Smart Clipboard**: Auto-captures copied text for instant processing.
- **Screen OCR**: Snipping tool to extract text from any screen area using LLM Vision.
- **Vision Chat**: Upload images or take screenshots and ask the AI questions about them.
- **Privacy Mode**: "Exclude Window" option to prevent the app from capturing itself (**Enabled by default** for enhanced security).

### 🤖 LLM Playground
- **Multi-Provider Support**: Switch seamlessy between **Gemini**, **OpenAI**, and **Claude**.
- **Enchant**: Instantly refine or polish text using AI templates.
- **Chat Interface**: Standard chat for brainstorming and assistance.

### 📚 Prompt Library
- **Organized Storage**: Save prompts with dynamic categories.
- **Template System**: Create reusable prompt templates.
- **Search**: Quickly find past history or saved prompts.

## Installation

### Prerequisites
```bash
# Core dependencies
pip install customtkinter pillow requests pyperclip packaging

# Optional: For enhanced functionality
pip install python-dotenv
```

### Setup
1. Clone or download the repository
2. Copy `.env.template` to `.env` (optional)
3. Add your API keys to `.env`:
```env
ANTHROPIC_API_KEY=your_claude_api_key
OPENAI_API_KEY=your_openai_api_key  
GEMINI_API_KEY=your_gemini_api_key
```

## Usage

### Starting the Application
```bash
python prompts_hub.py
```

## License

MIT License