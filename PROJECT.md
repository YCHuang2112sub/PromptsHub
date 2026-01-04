# 🧠 PromptsHub (AlphaMind Edition) - Project Documentation

## Project Overview
**PromptsHub**, codenamed **AlphaMind**, is a stylish, modern interface for intelligent prompt management and LLM interaction. It combines clipboard monitoring, screen OCR, and direct AI integration into a unified "Alicization" vision of human-AI symbiosis.

## Current Status
**Version**: v1.1 "Foundation"
**State**: ✅ Stable / 🚧 Active Development

We have successfully completed **Phase 1 (Stabilization & Core Integration)**.
-   ✅ **Environment Loading**: Automatic `.env.local` support.
-   ✅ **Gemini Integration**: Full Chat and Vision support using `gemini-1.5-flash`.
-   ✅ **Architecture**: Refactored `prompts_hub.py` to support real API calls.
-   ✅ **Licensing**: Apache 2.0 Licensed.

## Technical Stack
-   **Language**: Python 3.10+
-   **GUI**: Tkinter (Modern styling with custom theme)
-   **AI Providers**: Google Gemini (Primary), Anthropic Claude, OpenAI GPT-4
-   **Key Libraries**: `tk`, `Pillow` (Vision), `requests` (API), `dotenv` (Config)

---

## Future Implementation Phases

### Phase 2: Enhanced Prompt Management ("PromptGenie")
**Goal:** Make the prompt library dynamic and intelligent.
- [ ] **Dynamic Variable Injection**: Allow prompts to have variables beyond just `{text}` (e.g., `{tone}`, `{audience}`).
- [ ] **Category Management**: Implement the UI to add/edit/delete prompt categories.
- [ ] **Context-Aware Suggestions**: Analyze the copied text and suggest the best prompt from the library automatically.

### Phase 3: Advanced Data & Persistence
**Goal:** Improve how data is stored and retrieved.
- [ ] **Database Migration**: Move from flat JSON files to SQLite for better performance with thousands of items.
- [ ] **Search Improvements**: Implement fuzzy search and filtering by date/type/tags.
- [ ] **Export Formats**: Add PDF and Markdown export options.

### Phase 4: Cloud & Sync (Long Term)
**Goal:** Access your prompts and history everywhere.
- [ ] **Cloud Sync**: Optional synchronization with Google Drive or Dropbox.
- [ ] **Mobile Companion**: Interaction with the planned Android App.

## Immediate Next Steps
1.  **Audit Screen OCR**: Ensure the new `gemini-1.5-flash` integration for OCR behaves as expected in all multi-monitor setups.
2.  **Build Prompt Library**: The UI exists, but the backend logic for saving/loading custom prompts needs to be robustly implemented.
