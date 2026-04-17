# Strict Project Instructions & Corrections

## 1. Model Branding & Identity
- **Mandate**: The project MUST be branded as using **Gemini 2.5 Flash**.
- **Display**: All UI labels, footers, and engine status indicators must explicitly state "Gemini 2.5".
- **Backend Configuration**: The default model identifier in code and `.env` should be `gemini-2.5-flash`.

## 2. Ingestion & Vector Integrity
- **Anti-Hallucination Protocol**: Every time a new repository is ingested, the vector database (ChromaDB) MUST be completely cleared.
- **Logic**: In `src/api.py`, call `indexer.clear_vector_store()` before `indexer.index_files(files)`. This ensures context is scoped strictly to the current active repository.

## 3. UI/UX Functional Requirements
- **Quick Action Buttons**: The suggestion tags (e.g., "Explain Logic", "Find Bugs") must be functional. They should trigger the `handleSend` function with their label text as the prompt.
- **Persistence**: Suggestion tags must remain visible and interactive both before and after a repository is synchronized.
- **Accessibility**: Only core functional components should be interactive. Placeholders like "History" or "Settings" should either be removed or marked as "Coming Soon" to avoid user confusion.
- **Header**: Keep the top header clean. Do not display "Project Node" or versioning indicators in the center of the main chat header.

## 4. Technical Alignment
- **Ports**: Backend on `8000`, Frontend on `3000`.
- **IP Binding**: Use `127.0.0.1` for frontend-to-backend communication to avoid Windows-specific DNS resolution issues with `localhost`.
- **Backend Binding**: Use `0.0.0.0` for the backend server to ensure maximum accessibility across the local network.

## 5. Correction History
- **Fix (2026-04-16)**: Corrected `App.tsx` where `handleSend` logic was not correctly processing string inputs from quick-action tags.
- **Fix (2026-04-16)**: Implemented vector store purging in `src/api.py` to stop cross-repository hallucination.
- **Correction**: Replaced all mentions of Gemini 1.5 with Gemini 2.5 across the codebase.
