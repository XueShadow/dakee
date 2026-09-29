import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / '.env')

MAX_INPUT_LENGTH = int(os.getenv('MAX_INPUT_LENGTH', '15000'))
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', '5')) * 1024 * 1024
ALLOWED_EXTENSIONS = {'.txt', '.pdf', '.docx'}
AI_PROVIDER = os.getenv('AI_PROVIDER', 'local')
