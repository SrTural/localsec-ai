import ollama
from app.core.config import settings
from app.llm.prompts import SOC_SYSTEM_PROMPT
from app.core.logger import logger


class LogAnalyzer:
    def __init__(self):
        self.client = ollama.Client(host=settings.OLLAMA_HOST)
        self.model_name = settings.OLLAMA_MODEL

    def analyze(self, query: str, context_logs: list) -> str:
        context_text = "\n".join([
            f"[{log.get('timestamp')}] User: {log.get('user')} | IP: {log.get('ip')} | Event: {log.get('event_type')} | Msg: {log.get('raw_message')}"
            for log in context_logs
        ])
        prompt = f"LOGLAR:\n{context_text}\n\nSUAL: {query}"
        try:
            response = self.client.chat(
                model=self.model_name,
                messages=[
                    {'role': 'system', 'content': SOC_SYSTEM_PROMPT},
                    {'role': 'user', 'content': prompt}
                ],
                options={"temperature": 0.1}
            )
            return response['message']['content']
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            return f"AI xetasi: {str(e)}"
