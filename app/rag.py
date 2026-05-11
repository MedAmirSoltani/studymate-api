import chromadb
from chromadb.utils import embedding_functions
import pypdf
import os

# Initialize ChromaDB client (local persistent storage)
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Use OpenAI-compatible embeddings via Groq
# We use a local sentence-transformer for embeddings (free, no API call needed)
embedding_fn = embedding_functions.DefaultEmbeddingFunction()

# Get or create our collection (like a table in a regular DB)
collection = chroma_client.get_or_create_collection(
    name="studymate_docs",
    embedding_function=embedding_fn
)


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract raw text from PDF bytes."""
    import io
    reader = pypdf.PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """
    Split text into overlapping chunks.
    Why overlap? So we don't lose context at chunk boundaries.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap  # overlap with previous chunk
    return chunks


def add_document(file_bytes: bytes, filename: str) -> int:
    """Process a PDF and store its chunks in ChromaDB."""
    text = extract_text_from_pdf(file_bytes)
    chunks = chunk_text(text)

    # Add chunks to ChromaDB
    collection.add(
        documents=chunks,
        ids=[f"{filename}_chunk_{i}" for i in range(len(chunks))],
        metadatas=[{"source": filename, "chunk": i} for i in range(len(chunks))]
    )
    return len(chunks)


def retrieve_context(question: str, n_results: int = 3) -> str:
    """
    Find the most relevant chunks for a question.
    ChromaDB handles the similarity search automatically.
    """
    results = collection.query(
        query_texts=[question],
        n_results=n_results
    )
    # Join the top chunks into one context string
    chunks = results["documents"][0]
    sources = [m["source"] for m in results["metadatas"][0]]
    
    context = ""
    for i, (chunk, source) in enumerate(zip(chunks, sources)):
        context += f"[Source: {source}]\n{chunk}\n\n"
    
    return context