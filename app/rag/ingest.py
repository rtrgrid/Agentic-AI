from pypdf import PdfReader
import os

def load_pdf(path):
    """Loads a PDF and returns text with source metadata."""
    reader = PdfReader(path)
    filename = os.path.basename(path)

    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted

    return {
        "text": text,
        "source": filename
    }


def chunk_text(data, chunk_size=500, overlap=100):
    """Chunks text and attaches source metadata to each chunk."""
    text = data["text"]
    source = data["source"]
    
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk_content = text[start:end]
        
        # Attach metadata to the chunk string for the synthesizer
        full_chunk = f"[Source: {source}] {chunk_content}"
        chunks.append(full_chunk)

        start += chunk_size - overlap

    return chunks
