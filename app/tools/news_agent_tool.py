import requests

async def news_agent_tool(query: str) -> str:
    """Delegates to a specialized News Agent (A2A) to fetch the latest headlines on a topic.
    
    Args:
        query: The news topic to search for.
    """
    try:
        response = requests.get(
            "http://127.0.0.1:9000/news",
            params={
                "topic": query
            },
            timeout=10
        )
        data = response.json()
        return data.get("news", "No news found.")
    except Exception as e:
        return f"News Agent Error: {str(e)}"
