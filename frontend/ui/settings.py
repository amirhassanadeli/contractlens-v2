import os
from pathlib import Path

API_BASE_URL = os.getenv(
    "DJANGO_API_BASE_URL",
    "http://127.0.0.1:8000",
).rstrip("/")

SAMPLES_DIR = Path(__file__).resolve().parent.parent / "samples"

MAX_FILE_BYTES = 5 * 1024 * 1024
MAX_DOCUMENT_CHARS = 30_000

