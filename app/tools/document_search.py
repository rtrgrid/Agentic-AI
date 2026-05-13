from app.rag.vector_store import search

def document_search_tool(query):

    results = search(query)

    context = ""

    for i, result in enumerate(results):

        context += f"\n[Source {i+1}]\n"
        context += result
        context += "\n"

    return context