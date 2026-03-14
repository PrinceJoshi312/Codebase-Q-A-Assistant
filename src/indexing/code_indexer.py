import os
from pathlib import Path
from typing import List, Optional
from langchain_chroma import Chroma
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

class CodeIndexer:
    """Manages the indexing of codebase files into a vector store using LangChain."""

    def __init__(self, persist_directory: str = "./_chroma_db"):
        self.persist_directory = persist_directory
        # Local-First Embeddings (BGE-Small-EN-v1.5 by default)
        self.embeddings = FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5")
        
        # Initialize Vector Store
        self.vector_store = Chroma(
            collection_name="codebase_collection",
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory
        )

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
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Create basic document
                    doc = Document(
                        page_content=content,
                        metadata={
                            "source": str(file_path),
                            "filename": file_path.name,
                            "extension": file_path.suffix
                        }
                    )
                    
                    # Split and add to list
                    split_docs = text_splitter.split_documents([doc])
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
