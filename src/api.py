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
        # 1. Clone
        repo_path = ingestor.clone_repository(request.url, branch=request.branch)
        
        # 2. Analyze Structure
        repo_structure = ingestor.get_repo_structure(repo_path)
        entry_point = ingestor.detect_entry_point(repo_path)
        files = ingestor.get_codebase_files(repo_path)
        
        # 3. Initialize Indexer & Agent
        api_key = os.getenv("GOOGLE_API_KEY")
        # HARDCODE failsafe to prevent Pro usage
        model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        if "pro" in model_name.lower():
            model_name = "gemini-1.5-flash"
        
        print(f"DEBUG (API): Final model selected: {model_name}")
        
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0,
            google_api_key=api_key
        )
        
        indexer = CodeIndexer(llm=llm)
        indexer.index_files(files)
        
        agent = GeminiCodeAgent(
            indexer=indexer, 
            repo_structure=repo_structure, 
            entry_point=entry_point, 
            model_name=model_name
        )
        
        return {
            "status": "success",
            "repo_name": repo_path.name,
            "entry_point": entry_point,
            "file_count": len(files)
        }
    except Exception as e:
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
