import os
import groq
from dotenv import load_dotenv
from embed import get_embedding_model, query_vector_store
from chromadb import PersistentClient

# Load environment variables from .env file
load_dotenv()

def get_groq_client():
    """Initialize Groq client."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables")
    return groq.Groq(api_key=api_key)

def generate_answer(query, retrieved_chunks, client):
    """Generate a grounded answer using retrieved context."""
    # Build context from retrieved chunks
    context_parts = []
    sources = []
    for i, chunk in enumerate(retrieved_chunks["documents"][0]):
        source = retrieved_chunks["metadatas"][0][i]["source_file"]
        context_parts.append(f"[Document {i+1} from {source}]\n{chunk}")
        sources.append(source)
    
    context = "\n\n".join(context_parts)
    
    # Create prompt
    prompt = f"""You are a helpful assistant for Brooklyn College students. Answer the question using ONLY the provided context. Do not use outside knowledge. Always cite which document(s) your answer comes from.

Context:
{context}

Question: {query}

Answer:"""

    # Generate response
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",  
        messages=[
            {"role": "system", "content": "You are a helpful assistant that answers questions based only on provided context. Always cite your sources."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=500
    )
    
    answer = response.choices[0].message.content
    return answer, list(set(sources))  # Remove duplicate sources

def main():
    # Initialize
    client = get_groq_client()
    model = get_embedding_model()
    
    # Connect to existing vector store
    chroma_client = PersistentClient(path="./chroma_db")
    collection = chroma_client.get_collection("professor_reviews")
    
    # Interactive query loop
    print("Brooklyn College Professor RAG System")
    print("Type 'quit' to exit")
    print("-" * 50)
    
    while True:
        query = input("\nYour question: ").strip()
        if query.lower() in ["quit", "exit", "q"]:
            break
        
        if not query:
            continue
        
        # Retrieve relevant chunks
        results = query_vector_store(query, collection, model, n_results=5)
        
        # Generate answer
        answer, sources = generate_answer(query, results, client)
        
        print(f"\n{'='*50}")
        print(f"ANSWER:")
        print(f"{'='*50}")
        print(answer)
        print(f"\n{'='*50}")
        print(f"Sources: {', '.join(sources)}")
        print(f"{'='*50}")

if __name__ == "__main__":
    main()