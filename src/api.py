import os
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from src.ingestion.repo_ingestor import RepoIngestor
from src.indexing.code_indexer import CodeIndexer
from src.agent.gemini_agent import GeminiCodeAgent
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from fastapi.staticfiles import StaticFiles

load_dotenv(override=True)

app = FastAPI(title="Codebase Q&A Assistant API")

# Enable CORS for React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, set this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ... (rest of the shared instances and models)

# Shared Instances
ingestor = RepoIngestor()
indexer = None
agent = None
repo_structure = ""
entry_point = ""

class IngestRequest(BaseModel):
    url: str
    branch: Optional[str] = None

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def read_root():
    return {"status": "online", "message": "Codebase Q&A Assistant API is running"}

@app.post("/ingest")
async def ingest_repository(request: IngestRequest):
    global indexer, agent, repo_structure, entry_point
    
    try:
        print(f"[*] Ingestion Request Received for: {request.url}")
        
        # 1. Clone
        print(f"[*] Initializing Git Clone...")
        repo_path = ingestor.clone_repository(request.url, branch=request.branch)
        print(f"[*] Repository Cloned to: {repo_path}")
        
        # 2. Analyze Structure
        print(f"[*] Analyzing Repository Structure...")
        repo_structure = ingestor.get_repo_structure(repo_path)
        entry_point = ingestor.detect_entry_point(repo_path)
        files = ingestor.get_codebase_files(repo_path)
        print(f"[*] Analysis Complete. Found {len(files)} files.")
        
        # 3. Initialize Indexer & Agent
        api_key = os.getenv("GOOGLE_API_KEY")
        
        # Use gemini-2.5-flash as default as requested
        model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        
        print(f"[*] Initializing Neural Engine with model: {model_name}")
        
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0,
            google_api_key=api_key
        )
        
        # AGGRESSIVE CLEANUP: Wipe old data BEFORE initializing the engine
        indexer = CodeIndexer(llm=llm)
        print(f"[*] Performing Neural Flush (Clearing Vector Store)...")
        indexer.clear_vector_store()
        
        print(f"[*] Starting File Indexing...")
        indexer.index_files(files)
        
        print(f"[*] Initializing Gemini Code Agent...")
        agent = GeminiCodeAgent(
            indexer=indexer, 
            repo_structure=repo_structure, 
            entry_point=entry_point, 
            model_name=model_name
        )
        
        print(f"[*] Ingestion Successful for: {repo_path.name}")
        return {
            "status": "success",
            "repo_name": repo_path.name,
            "entry_point": entry_point,
            "file_count": len(files)
        }
    except Exception as e:
        print(f"[!] Ingestion Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/structure")
async def get_structure():
    if not repo_structure:
        raise HTTPException(status_code=400, detail="No repository ingested yet.")
    return {"structure": repo_structure}

@app.post("/chat")
async def chat(request: ChatRequest):
    if not agent:
        raise HTTPException(status_code=400, detail="Agent not initialized. Please ingest a repository first.")
    
    try:
        response = agent.ask(request.message)
        return {"response": response["output"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Serve static files from the frontend/dist directory
if os.path.exists("frontend/dist"):
    app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
