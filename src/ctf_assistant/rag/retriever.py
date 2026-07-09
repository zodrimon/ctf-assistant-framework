from typing import Dict, Any, List
from ctf_assistant.rag.store import KnowledgeStore

def retrieve_notes(query: str, n_results: int = 3) -> List[Dict[str, Any]]:
    """
    Retrieves the most relevant notes from the knowledge base for a given query.
    
    Args:
        query: The text to search for.
        n_results: Maximum number of results to return.
        
    Returns:
        A list of dictionaries containing 'text', 'metadata', and 'distance'.
    """
    if not query.strip():
        return []
        
    store = KnowledgeStore()
    results = store.query(query, n_results=n_results)
    
    notes = []
    
    # ChromaDB returns lists of lists because it supports querying multiple texts at once
    if not results or not results.get("documents") or not results["documents"][0]:
        return notes
        
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]
    
    for doc, meta, dist in zip(documents, metadatas, distances):
        notes.append({
            "text": doc,
            "metadata": meta,
            "distance": dist
        })
        
    return notes
