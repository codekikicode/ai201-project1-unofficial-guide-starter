from embed import get_embedding_model, query_vector_store
from chromadb import PersistentClient

model = get_embedding_model()
chroma_client = PersistentClient(path="./chroma_db")
collection = chroma_client.get_collection("professor_reviews")

test_queries = [
    "Which professor teaches CISC 3130?",
    "What do students say about Professor Gross?",
    "What is the best restaurant near Brooklyn College?"
]

for query in test_queries:
    print(f"\n{'='*60}")
    print(f"QUERY: {query}")
    print(f"{'='*60}")
    
    results = query_vector_store(query, collection, model, n_results=3)
    
    for i, doc in enumerate(results["documents"][0]):
        source = results["metadatas"][0][i]["source_file"]
        distance = results["distances"][0][i]
        print(f"\n--- Result {i+1} (distance: {distance:.4f}) ---")
        print(f"Source: {source}")
        print(f"Text: {doc[:250]}...")

print(f"\n{'='*60}")