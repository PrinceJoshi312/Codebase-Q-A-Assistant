# Tech Stack Guide: Codebase Q&A Assistant

This document provides a deep-dive overview of the technologies used in this project, explaining the "why" and "how" behind each selection.

---

## 1. Google Gemini 2.0 (LLM)
**What it is:** The "brain" of our application. It is a large language model (LLM) that can understand and generate human-like text and code.
- **Gemini 2.0 Flash:** Used for fast, high-volume tasks such as summarization and initial context filtering. Its low latency makes the app feel responsive.
- **Gemini 2.0 Pro (Experimental):** Used for the final generation step where deep code logic and cross-file reasoning are required. It handles the "thinking" part of the agent's work.
**Study Source:** [Google AI Studio Docs](https://ai.google.dev/gemini-api/docs)

## 2. LangChain (Orchestration Framework)
**What it is:** The "nervous system" of our application. It orchestrates the flow of data between the user, the LLM, and the various tools.
- **Tool-Calling Agent:** We use the `create_tool_calling_agent` pattern, which allows Gemini to autonomously decide when to search the codebase based on the user's question.
- **Prompts:** LangChain's `ChatPromptTemplate` helps us enforce strict "No Hallucination" rules.
**Study Source:** [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)

## 3. RAG (Retrieval-Augmented Generation)
**What it is:** A specialized "open-book" technique for AI. Instead of relying on the LLM's pre-trained knowledge, we provide it with the relevant snippets of *your* code before it generates an answer.
- **Retrieval:** Finding the right chunks of code in a massive repository.
- **Generation:** Using the LLM to synthesize those chunks into a coherent answer.
**Study Source:** [RAG for LLMs - Comprehensive Guide](https://www.ibm.com/topics/retrieval-augmented-generation)

## 4. Vector Stores & Local Embeddings (ChromaDB & FastEmbed)
**What it is:**
- **FastEmbed (Local):** We use the `BAAI/bge-small-en-v1.5` model to generate "embeddings" (number-based representations of text) locally. This is **free**, fast, and keeps your data secure.
- **ChromaDB:** A high-performance vector database that stores these embeddings and allows for "semantic search" (finding code by meaning, not just keywords).
**Study Source:** [ChromaDB Docs](https://docs.trychroma.com/) | [Qdrant FastEmbed](https://qdrant.github.io/fastembed/)

## 5. Recursive Character Text Splitter (Code-Aware)
**What it is:** A LangChain utility that splits large files into smaller "chunks."
- **Code Optimization:** Our splitter is configured with custom separators like `\nclass ` and `\ndef ` to ensure that functions and classes aren't cut in half, preserving their logical context for the LLM.
**Study Source:** [LangChain Text Splitters](https://python.langchain.com/docs/modules/data_connection/document_transformers/)

## 6. GitPython (Ingestion)
**What it is:** A library that allows Python to execute Git commands directly.
- **Usage:** It clones the specified repository to a temporary directory for processing and allows us to filter out unnecessary files like `.png` or `node_modules`.
**Study Source:** [GitPython Reference](https://gitpython.readthedocs.io/)
