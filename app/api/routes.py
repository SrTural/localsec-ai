from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from app.ingestion.parser import AuthLogParser
from app.ingestion.embedder import LogEmbedder
from app.ingestion.qdrant_client import QdrantManager
from app.llm.ollama_client import LogAnalyzer
from app.core.logger import logger

router = APIRouter()

parser = AuthLogParser()
embedder = LogEmbedder()
analyzer = LogAnalyzer()
qdrant_manager = None


def get_qdrant():
    global qdrant_manager
    if qdrant_manager is None:
        qdrant_manager = QdrantManager()
    return qdrant_manager


class QueryRequest(BaseModel):
    question: str
    limit: int = 5


@router.post("/ingest")
async def ingest_log_file(file: UploadFile = File(...)):
    if not file.filename.endswith(('.log', '.txt')):
        raise HTTPException(status_code=400, detail="Only .log or .txt files allowed.")
    content = await file.read()
    lines = content.decode('utf-8', errors='ignore').split('\n')
    parsed_logs = []
    for line in lines:
        if line.strip():
            parsed = parser.parse_line(line)
            if parsed:
                parsed_logs.append(parsed)
    if not parsed_logs:
        raise HTTPException(status_code=400, detail="No valid logs found.")
    embeddings = [embedder.create_embedding(log) for log in parsed_logs]
    get_qdrant().insert_logs(parsed_logs, embeddings)
    logger.info(f"Ingested {len(parsed_logs)} logs.")
    return {"status": "success", "ingested_count": len(parsed_logs)}


@router.post("/analyze")
async def analyze_logs(request: QueryRequest):
    query_vector = embedder.create_embedding({"user": "", "ip": "", "event_type": "", "message": request.question})
    context_logs = get_qdrant().search_logs(query_vector, limit=request.limit)
    if not context_logs:
        return {"answer": "No matching logs found. Please upload logs first."}
    answer = analyzer.analyze(request.question, context_logs)
    return {"question": request.question, "context_used": len(context_logs), "answer": answer}
