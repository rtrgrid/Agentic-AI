from app.rag.ingest import load_pdf, chunk_text
from app.rag.vector_store import add_documents

from app.agent import ask_agent


pdf_path = "app/data/research.pdf"

text = load_pdf(pdf_path)

chunks = chunk_text(text)

add_documents(chunks)

print("RAG Agent Ready!")

while True:

    query = input("\nAsk Question: ")

    if query.lower() == "exit":
        break

    answer = ask_agent(
            query,
            max_iterations=2
        )

    print("\nAnswer:")
    print(answer)