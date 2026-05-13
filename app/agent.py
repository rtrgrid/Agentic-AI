import asyncio
import json
import os
import sys
import vertexai
from functools import cached_property
from google.genai import Client
from google.adk.agents.llm_agent import Agent
from google.adk.models import Gemini, LlmRequest
from google.adk.tools.function_tool import FunctionTool
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

from app.tools.document_search import document_search_tool
from app.tools.web_search import web_search_tool
from app.tools.financial_tool import financial_data_tool
from app.tools.news_agent_tool import news_agent_tool
from app.tools.canvas_tool import canvas_tool
from app.critique import critique_response

# Initialize Vertex AI
vertexai.init(
    project="gd-gcp-internship-ds",
    location="us-central1"
)

# Custom Gemini class to force Vertex AI usage
class VertexGemini(Gemini):
    @cached_property
    def api_client(self) -> Client:
        return Client(
            vertexai=True,
            project="gd-gcp-internship-ds",
            location="us-central1"
        )

# Global logs for UI display
agent_logs = []

def log_event(event_type, message):
    log_entry = f"**{event_type}**: {message}"
    print(log_entry)
    agent_logs.append(log_entry)

# Define ADK Tools
tools = [
    FunctionTool(func=document_search_tool),
    FunctionTool(func=web_search_tool),
    FunctionTool(func=financial_data_tool),
    FunctionTool(func=news_agent_tool),
    FunctionTool(func=canvas_tool)
]

# Initialize the ADK Agent (Module 3 learning objective)
research_agent = Agent(
    name="ResearchAgent",
    model=VertexGemini(model="gemini-2.0-flash"),
    instruction="""
    You are an advanced autonomous research assistant powered by the Google ADK.
    
    Guidelines:
    1. For local company docs, use `document_search_tool`.
    2. For market data, use `financial_data_tool` (routed via MCP).
    3. For headlines, use `news_agent_tool` (A2A).
    4. For general web, use `web_search_tool`.
    5. For reports/code, use `canvas_tool`.
    """,
    tools=tools
)

# Set up the Runner
runner = Runner(
    app_name="ResearchApp",
    agent=research_agent,
    session_service=InMemorySessionService(),
    auto_create_session=True
)

async def _run_agent_to_completion(query, user_id, session_id):
    """Universal ADK event collector."""
    new_message = types.Content(
        parts=[types.Part(text=query)],
        role="user"
    )
    
    final_text = ""
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=new_message
    ):
        # Log tool calls
        if hasattr(event, 'get_function_calls'):
            try:
                f_calls = event.get_function_calls()
                if f_calls:
                    for fc in f_calls:
                        log_event("Execution", f"ADK calling tool: `{fc.name}`")
            except: pass

        # Extract text content
        if hasattr(event, 'content') and event.content and event.content.parts:
            for part in event.content.parts:
                if hasattr(part, 'text') and part.text:
                    final_text += part.text
                    
    return final_text

def _run_async(coro):
    """Universal async executor."""
    try:
        return asyncio.run(coro)
    except RuntimeError:
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            return executor.submit(asyncio.run, coro).result()

def ask_agent(query, max_iterations=3):
    global agent_logs
    agent_logs = []
    
    current_query = query
    final_answer = ""
    user_id = "default_user"
    session_id = "default_session"

    log_event("Starting", f"New ADK Research Request: '{query}'")

    for iteration in range(max_iterations):
        log_event("Iteration", f"Phase {iteration + 1}")
        
        try:
            # Step 1: ADK Plan & Execute
            final_answer = _run_async(_run_agent_to_completion(current_query, user_id, session_id))
            
            # Step 2: Critique (Phase 4 requirement)
            log_event("Critique", "Self-evaluating response quality...")
            critique = critique_response(query, final_answer)
            
            if "COMPLETE" in critique.upper():
                log_event("Status", "Response validated.")
                break
            elif "FOLLOW_UP:" in critique:
                follow_up = critique.split("FOLLOW_UP:")[-1].strip()
                log_event("Refining", f"Gap found: {follow_up}")
                current_query = f"Previous research was incomplete. Please find info on: {follow_up}. Update the answer."
            else:
                break
                
        except Exception as e:
            log_event("Error", str(e))
            final_answer = f"System error: {str(e)}"
            break

    return final_answer

def get_logs():
    return "\n\n".join(agent_logs)
