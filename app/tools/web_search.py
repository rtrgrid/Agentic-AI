from ddgs import DDGS


def web_search_tool(query, max_results=5):

    results_text = ""

    try:

        with DDGS() as ddgs:

            results = ddgs.text(
                query,
                max_results=max_results
            )

            for i, result in enumerate(results):

                if not result:
                    continue

                results_text += f"\n[Web Source {i+1}]\n"

                results_text += f"Title: {result.get('title', 'No Title')}\n"

                results_text += f"Body: {result.get('body', 'No Body')}\n"

                results_text += f"Link: {result.get('href', 'No Link')}\n\n"

    except Exception as e:

        results_text = f"Web search failed: {str(e)}"

    return results_text