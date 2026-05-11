import time
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from app.rag import add_document, retrieve_context
from app.llm import ask_llm
from app.monitoring import log_request, get_stats

app = FastAPI(
    title="StudyMate API",
    description="Upload course PDFs and ask questions about them.",
    version="1.0.0"
)


# --- Request/Response models ---

class QuestionRequest(BaseModel):
    question: str

class QuestionResponse(BaseModel):
    question: str
    answer: str
    latency_ms: float


# --- Endpoints ---

@app.get("/")
def root():
    return {"message": "StudyMate API is running"}


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a PDF and store it in ChromaDB.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    file_bytes = await file.read()
    num_chunks = add_document(file_bytes, file.filename)

    return {
        "message": f"Document '{file.filename}' uploaded successfully.",
        "chunks_stored": num_chunks
    }


@app.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """
    Ask a question. We retrieve relevant context from ChromaDB
    then pass it to the LLM to generate a grounded answer.
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    start = time.time()

    # Step 1 - Retrieve relevant chunks
    context = retrieve_context(request.question)

    # Step 2 - Generate answer
    answer = ask_llm(context, request.question)

    latency_ms = (time.time() - start) * 1000

    # Step 3 - Log the request (LLMOps)
    log_request(
        question=request.question,
        context_length=len(context),
        answer=answer,
        latency_ms=latency_ms,
        source_docs=list(set([
            line.replace("[Source: ", "").replace("]", "")
            for line in context.split("\n")
            if line.startswith("[Source:")
        ]))
    )

    return QuestionResponse(
        question=request.question,
        answer=answer,
        latency_ms=round(latency_ms, 2)
    )


@app.get("/stats")
def stats():
    """
    LLMOps monitoring endpoint.
    Returns basic stats about API usage.
    """
    return get_stats()