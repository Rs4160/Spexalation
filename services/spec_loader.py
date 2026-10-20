import re

from docx import Document
from pathlib import Path


def load_docx(file_path):
    """
    Read text from a 3GPP DOCX specification.
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Specification file not found: {file_path}"
        )

    document = Document(file_path)

    paragraphs = []

    for paragraph in document.paragraphs:

        text = paragraph.text.strip()

        if text:
            paragraphs.append(text)

    return paragraphs
def extract_clauses(paragraphs):
    """
    Convert 3GPP paragraphs into structured clauses.
    """

    clauses = []

    current_clause = None

    clause_pattern = re.compile(
        r"^(\d+(?:\.\d+)+)\s+(.+)$"
    )

    for paragraph in paragraphs:

        match = clause_pattern.match(paragraph)

        if match:
            clause_number = match.group(1)
            clause_title = match.group(2).strip()
            if re.search(r"\s+\d+$", clause_title):
                current_clause = None
                continue

            current_clause = {
                "number": clause_number,
                "title": clause_title,
                "paragraphs": [],
            }

            clauses.append(current_clause)

        elif current_clause:
            current_clause["paragraphs"].append(paragraph)

    return clauses