from typing import Any, Dict

try:
    from backend.app.providers.base import LocalProvider
    from backend.app.providers.base import AIProvider
    from backend.app.schemas.analysis import AnalysisResult
except ModuleNotFoundError:  # pragma: no cover - compatibility when run from backend package path
    from app.providers.base import LocalProvider
    from app.providers.base import AIProvider
    from app.schemas.analysis import AnalysisResult


class AnalysisService:
    def __init__(self, provider: AIProvider | None = None):
        self.provider = provider or LocalProvider()

    def analyze_text(self, text: str) -> Dict[str, Any]:
        payload = self.provider.analyze_text(text)
        result = AnalysisResult(**payload)
        return result.dict()
