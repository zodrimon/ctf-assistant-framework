import sys
from pathlib import Path
from typing import List
import pypdf

from ctf_assistant.rag.store import KnowledgeStore


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """
    Splits text into chunks of `chunk_size` characters with `overlap` characters of overlap.
    """
    if not text:
        return []
    
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


def extract_text(file_path: Path) -> str:
    """
    Extracts text from a given file (.md, .txt, .pdf).
    """
    ext = file_path.suffix.lower()
    
    if ext in [".md", ".txt"]:
        return file_path.read_text(encoding="utf-8")
        
    elif ext == ".pdf":
        text = ""
        try:
            reader = pypdf.PdfReader(file_path)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        except Exception as e:
            print(f"Error reading PDF {file_path}: {e}", file=sys.stderr)
            sys.exit(1)
        return text
        
    else:
        print(f"Unsupported file extension: {ext}", file=sys.stderr)
        sys.exit(1)


def ingest_file(file_path: Path):
    """
    Reads a file, chunks it, and ingests it into the ChromaDB KnowledgeStore.
    """
    if not file_path.exists():
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)
        
    print(f"[*] Extracting text from {file_path.name}...")
    text = extract_text(file_path)
    
    if not text.strip():
        print("Warning: No text could be extracted from the file.")
        return
        
    chunks = chunk_text(text)
    print(f"[*] Split text into {len(chunks)} chunks.")
    
    store = KnowledgeStore()
    
    for i, chunk in enumerate(chunks):
        doc_id = f"{file_path.name}-chunk-{i}"
        metadata = {
            "source": str(file_path.name),
            "chunk_index": i,
            "total_chunks": len(chunks)
        }
        store.add_document(doc_id=doc_id, text=chunk, metadata=metadata)
        
    print(f"[+] Successfully ingested {file_path.name} into the knowledge base.")
