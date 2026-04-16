import os
from pathlib import Path
from typing import List, Optional
from langchain_chroma import Chroma
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

class CodeIndexer:
    """Manages the indexing of codebase files into a vector store using LangChain."""

    def __init__(self, persist_directory: str = "./_chroma_db", llm=None):
        self.persist_directory = persist_directory
        # Local-First Embeddings (BGE-Small-EN-v1.5 by default)
        self.embeddings = FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5")
        self.llm = llm
        
        # Initialize Vector Store
        self.vector_store = Chroma(
            collection_name="codebase_collection",
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory
        )

    def clear_vector_store(self):
        """Removes the persistent Chroma DB directory."""
        if hasattr(self, 'vector_store') and self.vector_store is not None:
            # Attempt to release file handles by explicitly deleting the object
            del self.vector_store
            self.vector_store = None # Ensure it's marked as None
        
        if os.path.exists(self.persist_directory):
            try:
                import shutil
                shutil.rmtree(self.persist_directory)
                print(f"[*] Cleared existing vector store at {self.persist_directory}")
            except Exception as e:
                print(f"[!] Error clearing vector store: {e}")
        
        # Re-initialize the vector store to ensure it's empty after clearing
        # This is crucial even if rmtree failed, to ensure the object is in a valid state
        self.vector_store = Chroma(
            collection_name="codebase_collection",
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory
        )

    def generate_summary(self, file_path: Path, content: str):
        """Generates a short summary and module type of the file using the LLM."""
        if not self.llm:
            return "Summary not available (LLM not provided).", "unknown"
        
        prompt = f"""
        Analyze the following code file: {file_path}
        
        Provide:
        1. A 2-3 line summary of the file's purpose and logic.
        2. A module type (e.g., entrypoint, utility, model, library, configuration, etc.).
        
        Format the response exactly as:
        Summary: <summary>
        Module Type: <type>
        
        Code:
        {content[:4000]} 
        """
        try:
            response = self.llm.invoke(prompt)
            output = response.content.strip()
            
            summary = "N/A"
            module_type = "unknown"
            
            for line in output.split('\n'):
                if line.lower().startswith("summary:"):
                    summary = line.split(":", 1)[1].strip()
                elif line.lower().startswith("module type:"):
                    module_type = line.split(":", 1)[1].strip()
            
            return summary, module_type
        except Exception as e:
            return f"Error generating summary: {e}", "error"

    def index_files(self, file_paths: List[Path]):
        """Splits files into chunks and adds them to the vector store."""
        documents = []
        
        # Splitter optimized for code (respects common code separators)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            separators=["\nclass ", "\ndef ", "\n\n", "\n", " ", ""]
        )

        for file_path in file_paths:
            try:
                # Step 4: Safe File Reading - avoid UTF-8 crashes on partially invalid characters
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # Generate Summary and Module Type (Feature 2)
                    summary, module_type = self.generate_summary(file_path, content)
                    
                    # Create basic document
                    doc = Document(
                        page_content=content,
                        metadata={
                            "source": str(file_path),
                            "file_path": str(file_path),
                            "filename": file_path.name,
                            "extension": file_path.suffix,
                            "summary": summary,
                            "module_type": module_type
                        }
                    )
                    
                    # Split and add to list
                    split_docs = text_splitter.split_documents([doc])
                    # Ensure summary and module_type are in all chunks
                    for d in split_docs:
                        d.metadata["summary"] = summary
                        d.metadata["module_type"] = module_type
                        
                    documents.extend(split_docs)
            except Exception as e:
                print(f"[!] Error processing {file_path}: {e}")

        if documents:
            print(f"[*] Adding {len(documents)} chunks to the vector store...")
            self.vector_store.add_documents(documents)
            print("[*] Indexing complete.")
        else:
            print("[!] No documents found to index.")

    def search(self, query: str, k: int = 4) -> List[Document]:
        """Performs a semantic search for the most relevant code snippets."""
        return self.vector_store.similarity_search(query, k=k)

if __name__ == "__main__":
    # Quick test for US.2 (Semantic Search)
    indexer = CodeIndexer()
    # Assume a mock list of files for testing purposes
    # indexer.index_files([Path("src/ingestion/repo_ingestor.py")])
    # results = indexer.search("How do I clone a repository?")
    # for res in results:
    #     print(f"--- {res.metadata['source']} ---\n{res.page_content[:200]}...")
