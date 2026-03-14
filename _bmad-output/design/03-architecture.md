# Architecture: Codebase Q&A Assistant (Harden V2)

## 1. System Overview
The system employs an **Agentic RAG (Retrieval-Augmented Generation)** architecture with a **Code Knowledge Graph** layer. This allows the system to not only retrieve text but to traverse code dependencies (e.g., "Find all callers of this function") using the **Gemini 2.0** suite.

## 2. Latest Tech Stack
- **Language:** Python 3.12+
- **LLM Provider:** **Google Gemini 2.0 API**
  - `gemini-2.0-flash`: For high-throughput indexing, summarization, and initial retrieval.
  - `gemini-2.0-pro-exp-02-05`: For complex code reasoning, cross-file analysis, and final answer generation.
- **Orchestration:** `LlamaIndex` (Agentic Workflow) or `LangGraph`.
- **Embeddings (Local-First):** `FastEmbed` (by Qdrant) or `BGE-M3` running locally to minimize cost and latency during bulk indexing.
- **Vector + Graph Database:** `ChromaDB` for semantic search + `NetworkX` or `FalkorDB` for the **Code Dependency Graph**.
- **Parsing:** `Tree-sitter` for multi-language AST extraction.
- **Evaluation:** `RAGAS` + `Arize Phoenix` for automated tracing and accuracy benchmarking.

## 3. Advanced Component Breakdown

### 3.1 Agentic Ingestion & Graph Construction
- **Code Graph:** During ingestion, the system builds a directed graph of function calls and class inheritances.
- **Summarization:** Use `gemini-2.0-flash` to generate high-level "Module Summaries" stored as metadata to provide global project context.

### 3.2 Agentic Retrieval (Multi-Step)
- **Tool-Augmented Search:** Instead of simple vector lookup, the Gemini agent can invoke tools:
  - `search_code(query)`: Semantic vector search.
  - `find_references(symbol)`: Traverse the Code Graph for dependencies.
  - `get_file_structure()`: View directory tree.
- **Reranking:** Uses Gemini-based semantic reranking to prioritize the most relevant code snippets.

### 3.3 Evaluation & Observability
- **Traceability:** Every query is traced using OpenInference standards to identify retrieval gaps.
- **Self-Correction:** If the Gemini agent detects a "Low Confidence" retrieval, it automatically triggers a second, broader search step.

## 4. Scalability & Cost Controls
- **Gemini Flash Efficiency:** Offload 80% of routine tasks (summarization, simple queries) to `gemini-2.0-flash` to keep costs minimal.
- **Local Embeddings:** 100% of bulk indexing embeddings are generated locally.
- **Persistence:** SQL-backed state management for the indexing pipeline to allow "Resume from Checkpoint."

## 5. Security & Privacy
- **Gemini Safety Settings:** Strict configuration to ensure code isn't used for training (Enterprise/Vertex AI API settings).
- **Local Processing:** All code parsing and embedding generation happens on-prem/locally.
