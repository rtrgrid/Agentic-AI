import vertexai

from vertexai.generative_models import GenerativeModel

from app.tools.document_search import document_search_tool
from app.tools.web_search import web_search_tool
from app.tools.financial_tool import financial_data_tool
from app.critique import critique_response
from app.tools.news_agent_tool import news_agent_tool
from app.tools.canvas_tool import canvas_tool


vertexai.init(
    project="gd-gcp-internship-ds",
    location="us-central1"
)

model = GenerativeModel("gemini-2.0-flash")


def planner(query):

    query_lower = query.lower()

    # Financial Queries
    if any(word in query_lower for word in [
        "stock",
        "stocks",
        "crypto",
        "bitcoin",
        "ethereum",
        "currency",
        "forex",
        "usd",
        "eur",
        "market"
    ]):
        return "financial"

    # Document Queries
    elif any(word in query_lower for word in [
        "pdf",
        "document",
        "resume",
        "report"
    ]):
        return "document"
    
    # News-related queries
    elif any(word in query_lower for word in [
        "news",
        "headline",
        "latest updates",
        "breaking",
        "recent events"
    ]):
        return "news"
    
    # Canvas generation requests
    elif any(word in query_lower for word in [
        "report",
        "generate document",
        "summary",
        "markdown",
        "html",
        "code snippet",
        "write code"
    ]):
        return "canvas"

    # Web Queries
    elif any(word in query_lower for word in [
        "latest",
        "today",
        "news",
        "current"
    ]):
        return "web"

    return "both"

def ask_agent(query, max_iterations=2):

    current_query = query

    final_answer = ""

    for iteration in range(max_iterations):

        print(f"\n=== Research Iteration {iteration + 1} ===\n")

        answer = run_research(current_query)

        print("\n=== Generated Answer ===\n")

        print(answer)

        critique = critique_response(
            model,
            current_query,
            answer
        )

        print("\n=== Critique ===\n")

        print(critique)

        # Stop if critique says complete
        if "COMPLETE" in critique.upper():

            final_answer = answer

            break

        # Extract follow-up questions
        elif "FOLLOW_UP:" in critique:

            follow_up = critique.split(
                "FOLLOW_UP:"
            )[-1].strip()

            current_query = follow_up

            final_answer = answer

        else:

            final_answer = answer

            break

    return final_answer

def run_research(query):

    tool_choice = planner(query)

    context = ""

    if tool_choice == "financial":

        print("\nUsing Financial Data Tool...\n")

        context += financial_data_tool(query)

    elif tool_choice == "document":

        print("\nUsing Document Search...\n")

        context += document_search_tool(query)

    elif tool_choice == "web":

        print("\nUsing Web Search...\n")

        context += web_search_tool(query)
    elif tool_choice == "news":

        print("\nDelegating to News Agent...\n")

        context += news_agent_tool(query)
    elif tool_choice == "canvas":

        print("\nUsing Canvas Tool...\n")

        research_answer = web_search_tool(query)

        # Detect output format
        if "html" in query.lower():

            output_format = "html"

        elif "code" in query.lower():

            output_format = "code"

        else:

            output_format = "markdown"

        context += canvas_tool(
            output_type=output_format,
            title="AI Generated Report",
            content=research_answer,
            language="python"
        )

    else:

        print("\nUsing Hybrid Search...\n")

        context += "\n=== DOCUMENT SEARCH ===\n"

        context += document_search_tool(query)

        context += "\n=== WEB SEARCH ===\n"

        context += web_search_tool(query)

    prompt = f"""
    You are an advanced autonomous research assistant.

    Your responsibilities:
    - Analyze all evidence carefully
    - Combine information logically
    - Resolve conflicting evidence
    - Produce a clear final answer

    Context:
    {context}

    Question:
    {query}
    """

    response = model.generate_content(prompt)

    return response.text