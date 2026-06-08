import re

def chunk_document(doc, chunk_size=500, overlap=100):
    """Split a document into overlapping chunks."""
    text = doc["text"]
    chunks = []
    
    # Simple character-based chunking with overlap
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk_text = text[start:end]
        
        if end < len(text):
            # Look for sentence boundary in the last 50 chars
            search_start = max(start + chunk_size - 50, start)
            last_period = chunk_text.rfind('. ', search_start - start)
            last_newline = chunk_text.rfind('\n', search_start - start)
            
            break_point = max(last_period, last_newline)
            if break_point > chunk_size * 0.8:  # Only break if we have substantial content
                end = start + break_point + 1
                chunk_text = text[start:end]
        
        chunks.append({
            "id": f"{doc['id']}_chunk_{len(chunks)}",
            "text": chunk_text,
            "source": doc["id"],
            "metadata": {
                "source_file": doc["id"],
                "char_start": start,
                "char_end": end
            }
        })
        
        start = end - overlap  # Move forward with overlap
    
    return chunks

def chunk_all_documents(documents, chunk_size=500, overlap=100):
    """Chunk all documents."""
    all_chunks = []
    for doc in documents:
        chunks = chunk_document(doc, chunk_size, overlap)
        all_chunks.extend(chunks)
    return all_chunks

if __name__ == "__main__":
    from ingest import load_documents
    
    docs = load_documents()
    chunks = chunk_all_documents(docs)
    print(f"Created {len(chunks)} chunks from {len(docs)} documents")
    for chunk in chunks[:5]:
        print(f"  {chunk['id']}: {len(chunk['text'])} chars")