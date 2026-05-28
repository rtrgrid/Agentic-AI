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
from vertexai.generative_models import GenerativeModel

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

# Global logs for UI display
agent_logs = []

def log_event(event_type, message):
    log_entry = f"**{event_type}**: {message}"
    print(log_entry)
    agent_logs.append(log_entry)

# Custom Gemini class to force Vertex AI usage
class VertexGemini(Gemini):
    @cached_property
    def api_client(self) -> Client:
        return Client(
            vertexai=True,
            project="gd-gcp-internship-ds",
            location="us-central1"
        )

# ---------------------------------------------------
# COMPONENT 1: PLANNER (Phase 1 Requirement)
# ---------------------------------------------------
def planner(query, history=""):
    """Explicit planning step as mandated by Phase 1."""
    log_event("Planning", "Decomposing research task into tool calls...")
    
    planner_prompt = f"""
    You are an Autonomous Research Planner.
    Break down the user query into a list of specific tool calls.
    
    User Query: {query}
    Previous Context: {history}
    
    Available Tools:
    1. document_search_tool(query): Semantic search over private company documents.
    2. web_search_tool(query): General internet search for real-time info.
    3. financial_data_tool(category): Live market data. 'category' MUST be 'stocks', 'crypto', or 'currencies'.
    4. news_agent_tool(query): Latest headlines via sub-agent.
    5. canvas_tool(output_type, title, content, language): Generates reports/code. TRIGGER this when the user asks for a report, summary, or code snippet.
    
    Output a JSON list of tool calls:
    [
      {{"tool": "tool_name", "args": {{"arg_name": "value"}}, "reason": "why"}}
    ]
    """
    
    model = GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(
        planner_prompt,
        generation_config={"response_mime_type": "application/json"}
    )
    return json.loads(response.text)

# ---------------------------------------------------
# COMPONENT 2: EXECUTOR (Phase 1 & ADK Mandate)
# ---------------------------------------------------
# Define official ADK Tools
tools = [
    FunctionTool(func=document_search_tool),
    FunctionTool(func=web_search_tool),
    FunctionTool(func=financial_data_tool),
    FunctionTool(func=news_agent_tool),
    FunctionTool(func=canvas_tool)
]

# The ADK Agent acts as the Execution engine
research_executor = Agent(
    name="ExecutionAgent",
    model=VertexGemini(model="gemini-2.0-flash"),
    instruction="Execute the provided research plan using your tools. Return raw findings.",
    tools=tools
)

runner = Runner(
    app_name="ResearchApp",
    agent=research_executor,
    session_service=InMemorySessionService(),
    auto_create_session=True
)

async def _run_executor(query, user_id, session_id):
    """Universal ADK event collector."""
    new_message = types.Content(
        parts=[types.Part(text=query)],
        role="user"
    )
    
    raw_context = ""
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=new_message
    ):
        if hasattr(event, 'get_function_calls'):
            try:
                f_calls = event.get_function_calls()
                if f_calls:
                    for fc in f_calls:
                        log_event("Execution", f"ADK calling tool: `{fc.name}`")
            except: pass

        if hasattr(event, 'content') and event.content and event.content.parts:
            for part in event.content.parts:
                if hasattr(part, 'text') and part.text:
                    raw_context += part.text
                    
    return raw_context

# ---------------------------------------------------
# COMPONENT 3: SYNTHESIZER (Phase 1 & 2 Requirement)
# ---------------------------------------------------
def synthesiser(query, evidence, plan=None):
    """Explicit synthesis step with source reconciliation as mandated by Phase 2."""
    log_event("Synthesis", "Reconciling evidence and citing sources...")
    
    canvas_instruction = ""
    if plan and any(p.get("tool") == "canvas_tool" for p in plan):
        canvas_instruction = "The Planner triggered the Canvas tool. Ensure you prepare and present the Canvas input/output in the appropriate format (e.g., Markdown blocks, HTML rendering, or Code fences) as requested by the user."

    synth_prompt = f"""
    You are an expert Research Synthesizer.
    
    Query: {query}
    Evidence Collected: {evidence}
    
    Task:
    1. Produce a unified, coherent answer.
    2. Flag any conflicting information found in the sources.
    3. CITE sources explicitly (e.g., [Document Source 1], [Web Source 2]).
    4. Be professional and objective.
    5. {canvas_instruction}
    """
    
    model = GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(synth_prompt)
    return response.text

# ---------------------------------------------------
# MAIN AGENT LOOP (Phase 4)
# ---------------------------------------------------
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
    accumulated_context = ""
    final_answer = ""
    user_id = "default_user"
    session_id = "default_session"

    log_event("Starting", f"New ADK Research Request: '{query}'")

    for iteration in range(max_iterations):
        log_event("Iteration", f"Phase {iteration + 1}")
        
        try:
            # 1. Plan
            plan = planner(current_query, accumulated_context)
            plan_str = ", ".join([f"`{p['tool']}`" for p in plan])
            log_event("Planner", f"Executing: {plan_str}")
            
            # 2. Execute (via ADK)
            # We pass the plan to the ADK Agent to execute
            execution_query = f"Execute this plan: {json.dumps(plan)}"
            new_findings = _run_async(_run_executor(execution_query, user_id, session_id))
            accumulated_context += f"\n\nFindings from Phase {iteration+1}:\n{new_findings}"
            
            # 3. Synthesize
            final_answer = synthesiser(query, accumulated_context, plan)
            
            # 4. Critique
            log_event("Critique", "Self-evaluating response quality...")
            critique = critique_response(query, final_answer)
            
            if critique.get("complete"):
                log_event("Status", "Response validated and complete.")
                break
            else:
                follow_ups = critique.get("follow_ups", [])
                if not follow_ups:
                    break
                log_event("Refining", f"Found gaps: {', '.join(follow_ups)}")
                current_query = f"Original Query: {query}\nFollow-up research needed on: {follow_ups}"
                
        except Exception as e:
            log_event("Error", str(e))
            final_answer = f"System error: {str(e)}"
            break

    return final_answer

def get_logs():
    return "\n\n".join(agent_logs)
