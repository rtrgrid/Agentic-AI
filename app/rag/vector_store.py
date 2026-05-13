import faiss
import numpy as np

from app.rag.embeddings import get_embedding

documents = []

dimension = 384

index = faiss.IndexFlatL2(dimension)


def add_documents(chunks):

    global documents

    embeddings = []

    for chunk in chunks:

        embedding = get_embedding(chunk)

        embeddings.append(embedding)

        documents.append(chunk)

    embeddings = np.array(embeddings).astype("float32")

    index.add(embeddings)


def search(query, k=3):

    if len(documents) == 0:

        return ["No documents available"]

    query_embedding = np.array(
        [get_embedding(query)]
    ).astype("float32")

    distances, indices = index.search(
        query_embedding,
        min(k, len(documents))
    )

    results = []

    for idx in indices[0]:

        if idx < len(documents):

            results.append(documents[idx])

    return results