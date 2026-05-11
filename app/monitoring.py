import time
import json
import os
from datetime import datetime


LOG_FILE = "logs/requests.jsonl"


def ensure_log_dir():
    """Create logs directory if it doesn't exist."""
    os.makedirs("logs", exist_ok=True)


def log_request(
    question: str,
    context_length: int,
    answer: str,
    latency_ms: float,
    source_docs: list[str]
):
    """
    Log every RAG request with key LLMOps metrics.
    We use JSONL format (one JSON object per line) — easy to parse later.
    """
    ensure_log_dir()

    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "question": question,
        "answer_length": len(answer),
        "context_length": context_length,
        "latency_ms": round(latency_ms, 2),
        "source_docs": source_docs,
        "estimated_tokens": (context_length + len(answer)) // 4  # rough estimate
    }

    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")


def get_stats() -> dict:
    """
    Read logs and compute basic stats.
    In prod this would feed into Grafana/Datadog/Langfuse.
    """
    ensure_log_dir()

    if not os.path.exists(LOG_FILE):
        return {"total_requests": 0}

    entries = []
    with open(LOG_FILE, "r") as f:
        for line in f:
            entries.append(json.loads(line))

    if not entries:
        return {"total_requests": 0}

    latencies = [e["latency_ms"] for e in entries]
    tokens = [e["estimated_tokens"] for e in entries]

    return {
        "total_requests": len(entries),
        "avg_latency_ms": round(sum(latencies) / len(latencies), 2),
        "max_latency_ms": round(max(latencies), 2),
        "min_latency_ms": round(min(latencies), 2),
        "total_estimated_tokens": sum(tokens),
        "last_request": entries[-1]["timestamp"]
    }