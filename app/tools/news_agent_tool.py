import requests


def news_agent_tool(query):

    try:

        response = requests.get(
            "http://127.0.0.1:9000/news",
            params={
                "topic": query
            }
        )

        data = response.json()

        return data["news"]

    except Exception as e:

        return f"News Agent Error: {str(e)}"