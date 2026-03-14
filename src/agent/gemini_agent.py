import os
from typing import List, Optional
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from src.indexing.code_indexer import CodeIndexer

load_dotenv()

# Global Indexer Instance for the Agent's Tool
_indexer = None

@tool
def search_codebase(query: str) -> str:
    """Semantic search for relevant code snippets in the indexed repository."""
    if not _indexer:
        return "Error: Codebase indexer not initialized."
    
    results = _indexer.search(query, k=5)
    if not results:
        return "I couldn't find any relevant code for that query."
    
    formatted_results = []
    for doc in results:
        snippet = f"--- Source: {doc.metadata['source']} ---\n{doc.page_content}\n"
        formatted_results.append(snippet)
    
    return "\n".join(formatted_results)

class GeminiCodeAgent:
    """Agentic RAG implementation for Codebase Q&A using Gemini 2.0."""

    def __init__(self, indexer: CodeIndexer, model_name: str = "gemini-2.0-flash"):
        global _indexer
        _indexer = indexer
        
        # Initialize Gemini 2.0 Model
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
        
        # Define the Prompt with "No Hallucination" Guardrails
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an expert software engineer assistant for codebase analysis. "
                       "You must ONLY answer based on the context retrieved from the tools. "
                       "If the information is not available in the code, say 'I don't know.' "
                       "Always cite the file paths and line numbers if possible."),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])
        
        # Define Tools
        self.tools = [search_codebase]
        
        # Create the Agent
        self.agent = create_tool_calling_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(agent=self.agent, tools=self.tools, verbose=True)

    def ask(self, question: str):
        """Asks a question to the Gemini Code Agent."""
        return self.agent_executor.invoke({"input": question})

if __name__ == "__main__":
    # Test for US.3 (Explain this function)
    # indexer = CodeIndexer()
    # agent = GeminiCodeAgent(indexer)
    # response = agent.ask("How is the CLI entry point implemented in this repo?")
    # print(response['output'])
    pass
