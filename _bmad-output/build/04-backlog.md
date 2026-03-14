# Task Backlog: Codebase Q&A Assistant

## Epic 1: Repository Ingestion & Environment Setup
- **Story 1.1:** Initialize Python 3.12 project with `uv` or `poetry`.
- **Story 1.2:** Implement `RepoIngestor` using `GitPython` to clone public/private repos.
- **Story 1.3:** Create file filtering logic (respecting `.gitignore` and binary detection).

## Epic 2: Indexing Engine (Local-First)
- **Story 2.1:** Integrate `Tree-sitter` for language-aware AST parsing (Python/JS/Java).
- **Story 2.2:** Implement local embedding pipeline using `FastEmbed`.
- **Story 2.3:** Set up `ChromaDB` for vector storage and `NetworkX` for the Code Dependency Graph.
- **Story 2.4:** Implement incremental indexing (hashing files to skip unchanged content).

## Epic 3: Agentic Retrieval with Gemini
- **Story 3.1:** Integrate Gemini 2.0 API (`flash` and `pro-exp`).
- **Story 3.2:** Implement Agentic RAG tools (Semantic Search, Reference Finder, Structure Viewer).
- **Story 3.3:** Build the multi-step reasoning loop with `LlamaIndex` or `LangGraph`.

## Epic 4: Q&A Interface & Citations
- **Story 4.1:** Develop the CLI/Chat interface for natural language queries.
- **Story 4.2:** Implement source attribution and citation verification.
- **Story 4.3:** Add token usage and cost monitoring for Gemini API.

## Epic 5: Evaluation & Quality Assurance
- **Story 5.1:** Set up `RAGAS` and `Arize Phoenix` for trace analysis.
- **Story 5.2:** Create a "Ground Truth" test suite for codebase Q&A.
