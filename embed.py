import os
from dotenv import load_dotenv
load_dotenv()
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

def get_embedding_model():
    """Load the embedding model."""
    print(f"Loading embedding model: {EMBEDDING_MODEL}")
    return SentenceTransformer(EMBEDDING_MODEL)

def embed_chunks(chunks, model):
    """Generate embeddings for all chunks."""
    texts = [chunk["text"] for chunk in chunks]
    embeddings = model.encode(texts, show_progress_bar=True)
    
    for i, chunk in enumerate(chunks):
        chunk["embedding"] = embeddings[i].tolist()
    
    return chunks

def setup_vector_store(chunks, collection_name="professor_reviews"):
    """Store chunks in ChromaDB vector database."""
    # Initialize ChromaDB with persistent storage
    client = chromadb.PersistentClient(path="./chroma_db")
    
    # Delete prior collections (if they exist)
    try:
        client.delete_collection(collection_name)
    except:
        pass
    
    collection = client.create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )
    
    # Add documents to collection
    ids = [chunk["id"] for chunk in chunks]
    texts = [chunk["text"] for chunk in chunks]
    embeddings = [chunk["embedding"] for chunk in chunks]
    metadatas = [chunk["metadata"] for chunk in chunks]
    
    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas
    )
    
    print(f"Stored {len(chunks)} chunks in ChromaDB collection '{collection_name}'")
    return collection

def query_vector_store(query, collection, model, n_results=5):
    """Query the vector store for relevant chunks."""
    query_embedding = model.encode([query]).tolist()
    
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )
    
    return results

if __name__ == "__main__":
    from ingest import load_documents
    from chunk import chunk_all_documents
    
    # Load and chunk
    docs = load_documents()
    chunks = chunk_all_documents(docs)
    
    # Embed
    model = get_embedding_model()
    chunks = embed_chunks(chunks, model)
    
    # Store
    collection = setup_vector_store(chunks)
    
    # Test query
    print("\nTesting query: 'Which professor is the best for data structures?'")
    results = query_vector_store("Which professor is the best for data structures?", collection, model)
    
    for i, doc in enumerate(results["documents"][0]):
        print(f"\nResult {i+1} (distance: {results['distances'][0][i]:.4f}):")
        print(f"Source: {results['metadatas'][0][i]['source_file']}")
        print(f"Text: {doc[:200]}...")