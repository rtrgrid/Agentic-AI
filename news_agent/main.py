from fastapi import FastAPI

from ddgs import DDGS


app = FastAPI()


@app.get("/news")

def get_news(topic: str):

    results_text = ""

    try:

        with DDGS() as ddgs:

            results = ddgs.text(
                f"latest news about {topic}",
                max_results=5
            )

            for i, result in enumerate(results):

                if not result:
                    continue

                results_text += f"\n[News {i+1}]\n"

                results_text += f"Title: {result.get('title', 'No Title')}\n"

                results_text += f"Body: {result.get('body', 'No Body')}\n"

                results_text += f"Link: {result.get('href', 'No Link')}\n\n"

    except Exception as e:

        results_text = str(e)

    return {
        "topic": topic,
        "news": results_text
    }