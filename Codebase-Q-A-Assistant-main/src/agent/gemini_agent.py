import os
from typing import List, Optional
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from src.indexing.code_indexer import CodeIndexer

load_dotenv(override=True)

# Global Indexer Instance for the Agent's Tool
_indexer = None
_entry_point = "None detected"

@tool
def search_codebase(query: str) -> str:
    """Semantic search for relevant code snippets in the indexed repository."""
    if not _indexer:
        return "Error: Codebase indexer not initialized."
    
    # Feature 3: Retrieve top 10 chunks
    results = _indexer.search(query, k=10)
    if not results:
        return "I couldn't find any relevant code for that query."
    
    # ISSUE 1: Group by file and merge chunks
    grouped_results = {}
    for doc in results:
        source = doc.metadata.get('file_path', doc.metadata.get('source', 'unknown'))
        if source not in grouped_results:
            grouped_results[source] = {
                "summary": doc.metadata.get('summary', 'N/A'),
                "module_type": doc.metadata.get('module_type', 'unknown'),
                "chunks": []
            }
        grouped_results[source]["chunks"].append(doc.page_content)
    
    formatted_output = []
    for source, data in grouped_results.items():
        formatted_output.append(f"File: {source}")
        formatted_output.append(f"Summary: {data['summary']}")
        formatted_output.append(f"Module Type: {data['module_type']}")
        formatted_output.append("Relevant sections:")
        # Deduplicate and join chunks for a cleaner view
        unique_chunks = list(set(data['chunks']))
        for chunk in unique_chunks:
            # Clean up chunk to show relevant parts (simplified)
            formatted_output.append(f"* {chunk[:300]}...") 
        formatted_output.append("-" * 20)
    
    return "\n".join(formatted_output)

@tool
def generate_repo_summary(query: str = "") -> str:
    """Generates a high-level summary of the repository architecture, project type, and key modules."""
    if not _indexer or not _indexer.llm:
        return "Error: Codebase indexer or LLM not initialized."
    
    # Gather key information for the summary
    docs = _indexer.search("project architecture overview modules dependencies readme", k=15)
    
    context = "\n".join([
        f"File: {d.metadata.get('file_path', d.metadata.get('source'))}\n"
        f"Summary: {d.metadata.get('summary', 'N/A')}\n"
        f"Content: {d.page_content[:1000]}" 
        for d in docs
    ])
    
    # Access metadata from the global _indexer if needed, or assume it's passed via prompt
    # Since tools are functions, we'll rely on the agent's system prompt or passed context.
    
    prompt = f"""
    Based on the following context from the codebase, provide a structured repository summary.
    
    You MUST format your response with these exact sections:
    
    Repository: <name>
    
    Project Type
    <type>
    
    Architecture
    <architecture description>
    
    Project Structure
    <visual directory tree - use context provided if available>
    
    Entry Point
    <entry_point_file>
    
    Key Modules
    <List important files and their purpose>
    
    Dependencies
    <List main libraries used>
    
    Purpose
    <Overall project goal>

    Context:
    {context}
    """
    
    try:
        response = _indexer.llm.invoke(prompt)
        return response.content.strip()
    except Exception as e:
        return f"Error generating repo summary: {e}"

@tool
def generate_execution_flow(query: str = "") -> str:
    """Analyzes the repository and explains how the program runs step-by-step from the entry point. 
    Use this when the user asks 'How does this project work?', 'Explain execution flow', or 'How does the code run?'."""
    if not _indexer or not _indexer.llm:
        return "Error: Codebase indexer or LLM not initialized."
    
    global _entry_point
    
    # 1. Gather context from entry point and key modules
    search_query = f"entry point {_entry_point} execution flow main logic function calls imports"
    docs = _indexer.search(search_query, k=15)
    
    context = "\n".join([
        f"File: {d.metadata.get('file_path', d.metadata.get('source'))}\n"
        f"Summary: {d.metadata.get('summary', 'N/A')}\n"
        f"Module Type: {d.metadata.get('module_type', 'unknown')}\n"
        f"Content: {d.page_content[:1000]}" 
        for d in docs
    ])
    
    prompt = f"""
    Based on the following context from the codebase, explain the program's execution flow step-by-step.
    
    Analyze:
    - Entrypoint file: {_entry_point}
    - Imported modules and key function calls
    - Model/Data loading steps (if applicable)
    - Logical execution path (how data flows from start to finish)
    
    You MUST format your response EXACTLY as a flow diagram:
    
    Execution Flow

    Program Start
    ↓
    <Step 1: e.g., main.py loads configuration or model>
    
    ↓
    <Step 2: e.g., Server starts listening or user enters input>
    
    ↓
    <Step 3: e.g., Input is processed through functions A and B>
    
    ... (continue until the end)
    
    ↓
    <Final Step: e.g., Output is returned or displayed>

    Context:
    {context}
    
    Detected Entry Point: {_entry_point}
    """
    
    try:
        response = _indexer.llm.invoke(prompt)
        return response.content.strip()
    except Exception as e:
        return f"Error generating execution flow: {e}"

class GeminiCodeAgent:
    """Agentic RAG implementation for Codebase Q&A using Gemini 2.5."""

    def __init__(self, indexer: CodeIndexer, repo_structure: str = "", entry_point: str = "None detected", model_name: str = "gemini-2.5-flash"):
        global _indexer, _entry_point
        _indexer = indexer
        _entry_point = entry_point
        self.repo_structure = repo_structure
        self.entry_point = entry_point
        
        # Initialize Gemini Model
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        
        # Define the Prompt with Repository Structure (Feature 1) and Entry Point (Feature 3)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert software engineer assistant for codebase analysis. "
                       "You must ONLY answer based on the context retrieved from the tools. "
                       "If the information is not available in the code, say 'I don't know.' "
                       "Always cite the file paths and line numbers if possible.\n\n"
                       "Current Repository Structure:\n{repo_structure}\n\n"
                       "Detected Entry Point: {entry_point}"),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]).partial(repo_structure=self.repo_structure, entry_point=self.entry_point)
        
        # Define Tools (Execution flow tool added)
        self.tools = [search_codebase, generate_repo_summary, generate_execution_flow]
        
        # Create the Agent
        self.agent = create_tool_calling_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(agent=self.agent, tools=self.tools, verbose=False)

    def ask(self, question: str):
        """Asks a question to the Gemini Code Agent."""
        try:
            result = self.agent_executor.invoke({"input": question})
            output = result.get("output", "")
            
            # ISSUE 3: Handle raw agent output leaking (structured list vs clean text)
            if isinstance(output, list):
                clean_text = ""
                for part in output:
                    if isinstance(part, dict) and "text" in part:
                        clean_text += part["text"]
                    elif isinstance(part, str):
                        clean_text += part
                return {"output": clean_text.strip()}
            
            return {"output": str(output).strip()}
        except Exception as e:
            return {"output": f"Error: {str(e)}"}

if __name__ == "__main__":
    # Test for US.3 (Explain this function)
    # indexer = CodeIndexer()
    # agent = GeminiCodeAgent(indexer)
    # response = agent.ask("How is the CLI entry point implemented in this repo?")
    # print(response['output'])
    pass
