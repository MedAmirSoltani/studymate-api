# StudyMate API 📚

A production-grade RAG (Retrieval-Augmented Generation) API that lets you upload course PDFs and ask questions about them. Built with a full LLMOps stack.

## Architecture

```
User → FastAPI → ChromaDB (retrieval) → LLM (generation) → Response
                      ↓
                Monitoring layer (latency, tokens, logs)
```

## Tech Stack

| Layer | Technology |
|---|---|
| API | FastAPI |
| Vector DB | ChromaDB |
| LLM | Groq (openai/gpt-oss-120b) |
| Containerization | Docker + Docker Compose |
| CI/CD | GitHub Actions |
| Orchestration | Kubernetes (minikube) |
| IaC | Terraform |
| Monitoring | Custom LLMOps logger |

## Project Structure

```
studymate-api/
├── app/
│   ├── main.py          # FastAPI endpoints
│   ├── rag.py           # ChromaDB + retrieval logic
│   ├── llm.py           # Groq LLM client
│   └── monitoring.py    # LLMOps logging
├── tests/
│   └── test_api.py      # Pytest test suite
├── k8s/
│   ├── deployment.yaml  # K8s deployment (2 replicas)
│   ├── service.yaml     # K8s service (LoadBalancer)
│   └── configmap.yaml   # K8s config
├── terraform/
│   └── main.tf          # Infrastructure as Code
├── .github/
│   └── workflows/
│       └── ci.yml       # CI/CD pipeline
├── Dockerfile
└── docker-compose.yml
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| POST | `/upload` | Upload a PDF document |
| POST | `/ask` | Ask a question about uploaded docs |
| GET | `/stats` | LLMOps monitoring stats |

## Quick Start

### Local development

```bash
# Clone the repo
git clone https://github.com/MedAmirSoltani/studymate-api.git
cd studymate-api

# Install dependencies
pip install -r requirements.txt

# Add your Groq API key
echo "GROQ_API_KEY=your_key_here" > .env

# Run the app
uvicorn app.main:app --reload
```

Visit `http://localhost:8000/docs` for the interactive API docs.

### Docker Compose

```bash
docker compose up --build
```

### Kubernetes (minikube)

```bash
# Start minikube
minikube start --driver=docker

# Create secret
kubectl create secret generic studymate-secrets \
  --from-literal=GROQ_API_KEY=your_key_here

# Deploy
kubectl apply -f k8s/

# Access the service
minikube service studymate-service
```

## CI/CD Pipeline

Every push to `main` triggers:

1. **Test** — runs pytest suite (5 tests)
2. **Build** — builds Docker image
3. **Push** — pushes image to Docker Hub

If any test fails, the pipeline stops and nothing gets deployed.

## LLMOps Monitoring

Every request is logged to `logs/requests.jsonl` with:
- Timestamp
- Question
- Answer length
- Context length
- Latency (ms)
- Estimated token usage
- Source documents

Access live stats at `GET /stats`.
