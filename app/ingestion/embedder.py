import ollama
from app.core.config import settings

class LogEmbedder:
    def __init__(self):
        self.client = ollama.Client(host=settings.OLLAMA_HOST)
        self.model = settings.EMBEDDING_MODEL

    def create_embedding(self, log_data: dict) -> list[float]:
        text_to_embed = (
            f"User: {log_data.get('user')} "
            f"IP: {log_data.get('ip')} "
            f"Event: {log_data.get('event_type')} "
            f"Message: {log_data.get('message', log_data.get('raw_message', ''))}"
        )
        response = self.client.embeddings(model=self.model, prompt=text_to_embed)
        return response['embedding']