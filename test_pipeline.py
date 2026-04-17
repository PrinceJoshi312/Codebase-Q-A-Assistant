import os
from pathlib import Path
from src.ingestion.repo_ingestor import RepoIngestor
from src.indexing.code_indexer import CodeIndexer

def run_test():
    print("[*] Starting Pipeline Test...")
    
    # 1. Ingestion
    ingestor = RepoIngestor(temp_dir="./_test_repo")
    repo_url = "https://github.com/pallets/click"
    try:
        repo_path = ingestor.clone_repository(repo_url)
        files = ingestor.get_codebase_files(repo_path)
    except Exception as e:
        print(f"[!] Ingestion failed: {e}")
        return

    # 2. Indexing
    print("[*] Initializing Indexer...")
    indexer = CodeIndexer(persist_directory="./_test_chroma_db")
    
    # Index only a subset for speed if needed, but Click is small
    indexer.index_files(files)

    # 3. Verification Search
    query = "How is the Group class defined in click?"
    print(f"[*] Testing Search with Query: '{query}'")
    results = indexer.search(query, k=3)
    
    if results:
        print(f"[*] Found {len(results)} relevant snippets:")
        for i, doc in enumerate(results):
            print(f"\n--- Result {i+1} ({doc.metadata['source']}) ---")
            print(doc.page_content[:300] + "...")
    else:
        print("[!] No results found. Search failed.")

    # Cleanup (Optional)
    # ingestor.cleanup()

if __name__ == "__main__":
    run_test()
