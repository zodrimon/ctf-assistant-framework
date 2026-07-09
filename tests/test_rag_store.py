from pathlib import Path
from ctf_assistant.rag.store import KnowledgeStore

def test_knowledge_store_basic(tmp_path: Path):
    store = KnowledgeStore(db_path=tmp_path, collection_name="test_collection")
    
    # Initially empty
    results = store.query("test")
    assert len(results["documents"][0]) == 0
    
    # Add document
    store.add_document("doc1", "The password is super_secret_123", {"source": "notes.txt"})
    store.add_document("doc2", "The flag format is CTF{...}", {"source": "rules.md"})
    
    # Query for password
    results = store.query("What is the secret code?")
    docs = results["documents"][0]
    
    assert len(docs) > 0
    # "The password is super_secret_123" should be the most relevant
    assert "super_secret_123" in docs[0]
