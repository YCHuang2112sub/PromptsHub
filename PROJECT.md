# 🧠 PromptsHub (AlphaMind Edition) - Project Documentation

## Project Overview
**PromptsHub**, codenamed **AlphaMind**, is a stylish, modern interface for intelligent prompt management and LLM interaction. It combines clipboard monitoring, screen OCR, and direct AI integration into a unified "Alicization" vision of human-AI symbiosis.

## Current Status
**Version**: v2.0 "AlphaMind"
**State**: ✅ Stable / 🚧 Active Development

- [x] **Phase 1: Stabilization & Core Integration**
  - [x] Modular Architecture Refactor (AlphaMind Update)
  - [x] CustomTkinter GUI Migration
  - [x] Gemini/OpenAI/Claude Integration
  - [x] Basic History & Persistence

- [ ] **Phase 2: Enhanced Vision & Management** (Current Focus)
  - [x] **Advanced Vision**:
    - [x] Full Screen Screenshot
    - [x] Image Upload
    - [x] Vision Chat (Ask questions about images)
    - [x] Window Capture Exclusion (Privacy Mode)
  - [x] **Library Management**:
    - [x] Dynamic Categories (Add/Remove)
    - [x] Save Captured Text to Library
  - [x] **Refinement**:
    - [x] "Enchant" Text Logic (Polishing/Refining)

- [ ] **Phase 3: Advanced Data & Persistence**
  - [ ] Vector Database for Semantic Search
  - [ ] Cloud Sync / Export

## Technical Stack
-   **Language**: Python 3.10+
-   **GUI**: CustomTkinter (Modern Styling)
-   **AI Providers**: Google Gemini (Primary), Anthropic Claude, OpenAI GPT-4
-   **Key Libraries**: `customtkinter`, `Pillow` (Vision), `requests` (API), `dotenv` (Config), `pyperclip`

---

## Future Implementation Phases

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
1.  **Audit Screen OCR**: Ensure the new `gemini-2.5-flash` integration for OCR behaves as expected in all multi-monitor setups.
2.  **Build Prompt Library**: The UI exists, but the backend logic for saving/loading custom prompts needs to be robustly implemented.
