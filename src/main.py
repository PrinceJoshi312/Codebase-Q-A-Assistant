import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from src.ingestion.repo_ingestor import RepoIngestor
from src.indexing.code_indexer import CodeIndexer
from src.agent.gemini_agent import GeminiCodeAgent

def main():
    load_dotenv(override=True)
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("[!] Error: GOOGLE_API_KEY not found in environment. Please set it in a .env file.")
        sys.exit(1)

    print("="*50)
    print("      CODEBASE Q&A ASSISTANT (BMAD V6)      ")
    print("="*50)

    # 1. Setup Phase
    repo_url = "https://github.com/PrinceJoshi312/PrinceJoshi312"
    print(f"\n[>] Using hardcoded GitHub Repository URL: {repo_url}")
    if not repo_url:
        print("[!] No URL provided. Exiting.")
        return

    # Initialize LLM for Summarization and Agent
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    print(f"DEBUG: Model name being used: {model_name}")
    llm = ChatGoogleGenerativeAI(
        model=model_name,
        temperature=0,
        google_api_key=api_key
    )

    ingestor = RepoIngestor()
    indexer = CodeIndexer(llm=llm)
    
    try:
        # 2. Ingestion & Indexing Phase
        print(f"\n[*] Initializing Analysis for: {repo_url} with model: {model_name}")
        repo_path = ingestor.clone_repository(repo_url)
        files = ingestor.get_codebase_files(repo_path)
        
        # Feature 1: Get Repository Structure
        repo_structure = ingestor.get_repo_structure(repo_path)
        print("\n[*] Repository Structure Detected:")
        print(repo_structure)
        
        # Feature 3: Detect Entry Point
        entry_point = ingestor.detect_entry_point(repo_path)
        print(f"[*] Entry Point Detected: {entry_point}")
        
        print("\n[*] Indexing codebase with file summarization... This may take a moment.")
        indexer.clear_vector_store()
        indexer.index_files(files)
        
        # 3. Agent Initialization
        print("[*] Booting Gemini Code Agent...")
        agent = GeminiCodeAgent(indexer, repo_structure=repo_structure, entry_point=entry_point, model_name=model_name)
        
        # 4. Interactive Chat Loop
        print("\n" + "="*50)
        print("  CHAT INITIALIZED - Type 'exit' to quit  ")
        print("="*50)
        
        print("\nSuggested Queries:")
        print("1. What does this repository do?")
        print("2. Explain a feature in this repository")
        print("3. Show me important files")
        print("4. How does this project work?")
        
        while True:
            user_input = input("\n[User]: ").strip()
            
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("\n[*] Shutting down. Goodbye!")
                break
                
            if not user_input:
                continue

            # ISSUE 1: Intent Mapping for numeric selections
            if user_input == "1":
                user_input = "What does this repository do?"
                print(f"[System]: Mapping '1' -> '{user_input}'")
            elif user_input == "2":
                user_input = "Explain a feature in this repository"
                print(f"[System]: Mapping '2' -> '{user_input}'")
            elif user_input == "3":
                user_input = "Show me important files"
                print(f"[System]: Mapping '3' -> '{user_input}'")
            elif user_input == "4":
                user_input = "How does this project work?"
                print(f"[System]: Mapping '4' -> '{user_input}'")

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
