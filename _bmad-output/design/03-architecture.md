# System Architecture: Agentic RAG Codebase Assistant

This document outlines the high-level architecture of the Codebase Q&A Assistant, detailing how it transforms a raw GitHub repository into an interactive, AI-driven knowledge base.

## 1. Architectural Strategy
The system employs an **Agentic RAG (Retrieval-Augmented Generation)** architecture with a **Code Knowledge Graph** layer. This allows the system to not only retrieve text but to traverse code dependencies (e.g., "Find all callers of this function") using **Google Gemini**.

## 2. Core Components

### A. LLM Provider (The Brain)
- **LLM Provider:** **Google Gemini API**
- **Gemini 2.5 Flash:** Used for complex code reasoning, cross-file analysis, and final answer generation. It provides a strong balance of intelligence and efficiency.

### B. Ingestion & Pre-processing (The Digestive System)
- **Git Ingestion:** Clones repositories while filtering out large binaries, hidden files, and environment-specific folders.
- **Code-Aware Chunking:** Uses **LangChain's RecursiveCharacterTextSplitter** with language-specific separators (`class`, `def`, `export`) to maintain logical context.

### C. Vector Store & Retrieval (The Memory)
- **Local Embeddings:** Uses **FastEmbed** to generate semantic vectors locally, ensuring that private code never leaves the machine for indexing.
- **ChromaDB:** A persistent local vector store for low-latency retrieval of relevant code chunks.

## 3. Advanced Reasoning Features
- **Summarization:** Use LLM to generate high-level "Module Summaries" stored as metadata to provide global project context.
- **Tool-Augmented Search:** Instead of simple vector lookup, the agent can invoke tools to find files, functions, and cross-references.
- **Reranking:** Uses semantic reranking to prioritize the most relevant code snippets for the final answer.
- **Self-Correction:** If the agent detects a "Low Confidence" retrieval, it automatically triggers a second, broader search step.

## 4. Security & Privacy
- **Local Indexing:** Embeddings and vector storage are 100% local.
- **Gemini Safety Settings:** Configured to ensure optimal performance while respecting the provided context limits.
- **Secret Scrubbing:** Pre-processing steps to ensure `.env` files and hardcoded secrets are not indexed.
