import os
from pathlib import Path
from typing import Dict, List, Any, Optional

import chromadb
from chromadb.utils import embedding_functions


class KnowledgeStore:
    """
    Manages local RAG document storage using ChromaDB.
    Uses the default ONNX-based all-MiniLM-L6-v2 model for embeddings to balance size and accuracy.
    """

    def __init__(self, db_path: Optional[str | Path] = None, collection_name: str = "ctf_knowledge"):
        # By default, store in ~/.ctf-assistant/chroma_db
        if db_path is None:
            home = Path.home()
            self.db_path = home / ".ctf-assistant" / "chroma_db"
        else:
            self.db_path = Path(db_path)
            
        self.db_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize persistent ChromaDB client
        self.client = chromadb.PersistentClient(path=str(self.db_path))
        
        # Using default ONNX-based all-MiniLM-L6-v2 embedding function provided by Chroma
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
        
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"}
        )

    def add_document(self, doc_id: str, text: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add a document to the collection.
        """
        self.collection.add(
            ids=[doc_id],
            documents=[text],
            metadatas=[metadata or {}]
        )

    def query(self, query_text: str, n_results: int = 3) -> Dict[str, Any]:
        """
        Query the collection for the most relevant documents.
        """
        if self.collection.count() == 0:
            return {"documents": [[]], "metadatas": [[]], "distances": [[]]}
            
        results = self.collection.query(
            query_texts=[query_text],
            n_results=min(n_results, self.collection.count())
        )
        return results
