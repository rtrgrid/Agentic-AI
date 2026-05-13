from app.rag.vector_store import search

async def document_search_tool(query: str) -> str:
    """Searches local PDF documents for information (e.g., reports, resumes, company docs).
    
    Args:
        query: The semantic search query.
    """
    results = search(query)

    context = ""
    for i, result in enumerate(results):
        context += f"\n[Document Source {i+1}]\n"
        context += result
        context += "\n"

    return context
