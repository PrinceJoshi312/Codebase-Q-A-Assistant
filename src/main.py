import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from src.ingestion.repo_ingestor import RepoIngestor
from src.indexing.code_indexer import CodeIndexer
from src.agent.gemini_agent.py import GeminiCodeAgent

def main():
    load_dotenv()
    if not os.getenv("GOOGLE_API_KEY"):
        print("[!] Error: GOOGLE_API_KEY not found in environment. Please set it in a .env file.")
        sys.exit(1)

    print("="*50)
    print("      CODEBASE Q&A ASSISTANT (BMAD V6)      ")
    print("="*50)

    # 1. Setup Phase
    repo_url = input("\n[>] Enter GitHub Repository URL: ").strip()
    if not repo_url:
        print("[!] No URL provided. Exiting.")
        return

    ingestor = RepoIngestor()
    indexer = CodeIndexer()
    
    try:
        # 2. Ingestion & Indexing Phase
        print(f"\n[*] Initializing Analysis for: {repo_url}")
        repo_path = ingestor.clone_repository(repo_url)
        files = ingestor.get_codebase_files(repo_path)
        
        print("[*] Indexing codebase... This may take a moment.")
        indexer.index_files(files)
        
        # 3. Agent Initialization
        print("[*] Booting Gemini 2.0 Code Agent...")
        agent = GeminiCodeAgent(indexer)
        
        # 4. Interactive Chat Loop
        print("\n" + "="*50)
        print("  CHAT INITIALIZED - Type 'exit' to quit  ")
        print("="*50)
        
        while True:
            user_input = input("\n[User]: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("\n[*] Shutting down. Goodbye!")
                break
                
            if not user_input:
                continue

            print("\n[Gemini]: Thinking...")
            try:
                response = agent.ask(user_input)
                print(f"\n[Gemini]: {response['output']}")
            except Exception as e:
                print(f"\n[!] Error during query: {e}")

    except Exception as e:
        print(f"\n[!] Fatal Error: {e}")
    finally:
        # Optional: Ask user if they want to keep the local repo/index
        # ingestor.cleanup()
        pass

if __name__ == "__main__":
    main()
