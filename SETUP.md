# 🚀 Cross-Platform Setup Guide

## 📦 1. Install Dependencies

### All Platforms:
```bash
pip install keyboard pyperclip Pillow requests
```

### Platform-Specific Notes:
- **Windows**: May need Visual C++ Redistributable
- **Linux**: May need `sudo apt-get install python3-tk python3-dev`
- **macOS**: Built-in Python may need `pip3` instead of `pip`
- **Android (Termux)**: `pkg install python python-tkinter`

## 🔑 2. Setup API Keys (Choose Your Platform)

### Method 1: Using .env File (Recommended)
```bash
# Copy template
cp .env.template .env

# Edit .env with your preferred text editor
# Windows: notepad .env
# Linux/Mac: nano .env
```

Add your API key to `.env`:
```bash
# Choose ONE provider:
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
# OR
OPENAI_API_KEY=sk-your-openai-key-here  
# OR
GOOGLE_API_KEY=your-gemini-key-here
```

### Method 2: Environment Variables

#### Windows (PowerShell):
```powershell
# Temporary (current session only)
$env:ANTHROPIC_API_KEY = "sk-ant-your-key-here"

# Permanent (survives restart)
setx ANTHROPIC_API_KEY "sk-ant-your-key-here"
```

#### Windows (Command Prompt):
```cmd
# Permanent
setx ANTHROPIC_API_KEY "sk-ant-your-key-here"
```

#### Linux/Mac (Bash/Zsh):
```bash
# Temporary
export ANTHROPIC_API_KEY="sk-ant-your-key-here"

# Permanent (add to ~/.bashrc or ~/.zshrc)
echo 'export ANTHROPIC_API_KEY="sk-ant-your-key-here"' >> ~/.bashrc
source ~/.bashrc
```

#### Android (Termux):
```bash
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
# Add to ~/.bashrc for persistence
echo 'export ANTHROPIC_API_KEY="sk-ant-your-key-here"' >> ~/.bashrc
```

## 🚀 3. Run the Program

### All Platforms:
```bash
python clipboard_ocr_manager.py
```

### Alternative Python Commands:
- **Windows**: `py clipboard_ocr_manager.py`
- **Linux/Mac**: `python3 clipboard_ocr_manager.py`
- **If in PATH**: Just double-click the `.py` file

## 🔑 Where to Get API Keys

| Provider | URL | Cost | Best For |
|----------|-----|------|----------|
| **Claude** | https://console.anthropic.com/ | Pay-per-use | OCR, text analysis |
| **OpenAI** | https://platform.openai.com/api-keys | Pay-per-use | Code analysis |  
| **Gemini** | https://makersuite.google.com/app/apikey | Free tier | General use |

### API Key Formats:
- **Claude**: `sk-ant-api03-...` (starts with `sk-ant-`)
- **OpenAI**: `sk-proj-...` or `sk-...` (starts with `sk-`)
- **Gemini**: `AIza...` (starts with `AIza`)

## ✅ Platform-Specific First Run

### Windows:
1. ✅ Run PowerShell as Administrator (for keyboard monitoring)
2. ✅ Install dependencies: `pip install keyboard pyperclip Pillow requests`
3. ✅ Set API key: `$env:ANTHROPIC_API_KEY = "your-key"`
4. ✅ Run: `python clipboard_ocr_manager.py`
5. ✅ Test Ctrl+C (copy some text anywhere)

### Linux:
1. ✅ Install system deps: `sudo apt-get install python3-tk python3-dev`
2. ✅ Install Python deps: `pip3 install keyboard pyperclip Pillow requests`
3. ✅ Set API key: `export ANTHROPIC_API_KEY="your-key"`
4. ✅ Run: `python3 clipboard_ocr_manager.py`
5. ✅ May need `sudo` for global keyboard monitoring

### macOS:
1. ✅ Install dependencies: `pip3 install keyboard pyperclip Pillow requests`
2. ✅ Set API key: `export ANTHROPIC_API_KEY="your-key"`
3. ✅ Grant accessibility permissions when prompted
4. ✅ Run: `python3 clipboard_ocr_manager.py`

### Android (Termux):
1. ✅ Install Termux from F-Droid (not Play Store)
2. ✅ `pkg install python python-tkinter`
3. ✅ `pip install keyboard pyperclip Pillow requests`
4. ✅ `export ANTHROPIC_API_KEY="your-key"`
5. ✅ Enable X11 forwarding: `pkg install x11-repo`

## 🐛 Platform-Specific Troubleshooting

### Windows Issues:
- **"Access denied"**: Run PowerShell as Administrator
- **"keyboard not working"**: Try running as Administrator
- **"Module not found"**: Use `py -m pip install` instead of `pip`

### Linux Issues:
- **"No module named '_tkinter'"**: `sudo apt-get install python3-tk`
- **"Permission denied"**: May need `sudo` for global hotkeys
- **"Display not found"**: Set `export DISPLAY=:0`

### macOS Issues:
- **"Accessibility permissions"**: System Preferences → Security → Accessibility
- **"Command not found"**: Use `python3` and `pip3`
- **"Certificate errors"**: Update certificates or use `--trusted-host`

### Android Issues:
- **"GUI not working"**: Install VNC server or use X11 forwarding
- **"Keyboard monitoring"**: Limited on Android, may not work fully
- **"Storage permissions"**: Grant Termux storage access

## 🔒 Security Best Practices

- **Never share API keys** or commit them to version control
- **Use .env files** for development (already in .gitignore)
- **Set environment variables** for production
- **Monitor API usage** to avoid unexpected charges
- **Rotate keys** regularly for security

## 🎉 Success Indicators

You'll know it's working when you see:
```
Loaded 1 environment variables from .env file
Clipboard & OCR Manager started
Using CLAUDE API
● Monitoring Ctrl+C
```

Then test by copying any text (Ctrl+C) - it should appear in the Live Capture panel!