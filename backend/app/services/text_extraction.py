from pathlib import Path
from typing import Optional

from pypdf import PdfReader
from docx import Document

try:
    from backend.app.core.config import ALLOWED_EXTENSIONS
except ModuleNotFoundError:  # pragma: no cover - compatibility when run from backend package path
    from app.core.config import ALLOWED_EXTENSIONS


def extract_text(file_path: str) -> str:
    suffix = Path(file_path).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise ValueError('Unsupported file type. Please upload a .txt, .pdf, or .docx file.')

    if suffix == '.txt':
        return Path(file_path).read_text(encoding='utf-8', errors='ignore')

    if suffix == '.pdf':
        reader = PdfReader(file_path)
        pages = [page.extract_text() or '' for page in reader.pages]
        return '\n'.join(pages).strip()

    if suffix == '.docx':
        document = Document(file_path)
        paragraphs = [paragraph.text for paragraph in document.paragraphs]
        return '\n'.join(paragraphs).strip()

    raise ValueError('Unable to extract text from the uploaded file.')


def validate_file(file_name: Optional[str], file_size: Optional[int]) -> None:
    if not file_name:
        raise ValueError('No file was provided.')

    suffix = Path(file_name).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise ValueError('Unsupported file type. Please upload a .txt, .pdf, or .docx file.')

    if file_size is None or file_size <= 0:
        raise ValueError('The uploaded file is empty.')

    max_size = 5 * 1024 * 1024
    if file_size > max_size:
        raise ValueError('The uploaded file exceeds the 5 MB limit.')
