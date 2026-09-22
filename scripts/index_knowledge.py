from pathlib import Path
from src.rag.service import index_documents


def chunks(text: str, size: int = 900):
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    current = ""
    for p in paragraphs:
        if current and len(current) + len(p) > size:
            yield current
            current = p
        else:
            current = (current + "\n\n" + p).strip()
    if current:
        yield current


docs = []
for path in Path("docs").glob("*.md"):
    for chunk in chunks(path.read_text()):
        docs.append((path.name, chunk))
print({"indexed": index_documents(docs)})
