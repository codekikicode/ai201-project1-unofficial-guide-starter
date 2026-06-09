import numpy as np
from rank_bm25 import BM25Okapi
from embed import get_embedding_model, query_vector_store
from chromadb import PersistentClient
import re

def tokenize(text):
    """Simple tokenizer for BM25."""
    return re.findall(r'\b\w+\b', text.lower())

class HybridSearcher:
    def __init__(self, collection, model, alpha=0.5):
        """
        alpha: weight for semantic score (0=BM25 only, 1=semantic only)
        """
        self.collection = collection
        self.model = model
        self.alpha = alpha
        
        # Build BM25 index
        self._build_bm25()
    
    def _build_bm25(self):
        """Build BM25 index from all documents in collection."""
        all_docs = self.collection.get(include=["documents", "metadatas"])
        self.doc_ids = all_docs["ids"]
        self.doc_texts = all_docs["documents"]
        self.doc_metadatas = all_docs["metadatas"]
        
        # Tokenize for BM25
        self.tokenized_docs = [tokenize(doc) for doc in self.doc_texts]
        self.bm25 = BM25Okapi(self.tokenized_docs)
        
        print(f"Built BM25 index with {len(self.doc_ids)} documents")
    
    def search(self, query, n_results=5):
        """Hybrid search combining semantic and BM25 scores."""
        # Semantic search
        semantic_results = query_vector_store(query, self.collection, self.model, n_results=len(self.doc_ids))
        
        # BM25 search
        tokenized_query = tokenize(query)
        bm25_scores = self.bm25.get_scores(tokenized_query)
        
        # Normalize scores
        semantic_scores = np.array(semantic_results["distances"][0])
        
        # Convert distances to similarities (lower distance = higher similarity)
        semantic_sims = 1 - (semantic_scores / np.max(semantic_scores) if np.max(semantic_scores) > 0 else semantic_scores)
        
        bm25_sims = bm25_scores / np.max(bm25_scores) if np.max(bm25_scores) > 0 else bm25_scores
        
        # Combine scores
        combined_scores = {}
        for i, doc_id in enumerate(semantic_results["ids"][0]):
            combined_scores[doc_id] = {
                "semantic": semantic_sims[i],
                "bm25": 0,
                "combined": self.alpha * semantic_sims[i]
            }
        
        for i, doc_id in enumerate(self.doc_ids):
            if doc_id in combined_scores:
                combined_scores[doc_id]["bm25"] = bm25_sims[i]
                combined_scores[doc_id]["combined"] += (1 - self.alpha) * bm25_sims[i]
            else:
                combined_scores[doc_id] = {
                    "semantic": 0,
                    "bm25": bm25_sims[i],
                    "combined": (1 - self.alpha) * bm25_sims[i]
                }
        
        # Sort by combined score
        sorted_results = sorted(combined_scores.items(), key=lambda x: x[1]["combined"], reverse=True)
        
        # Format results like ChromaDB query output
        top_ids = [doc_id for doc_id, _ in sorted_results[:n_results]]
        documents = []
        metadatas = []
        distances = []
        
        for doc_id in top_ids:
            idx = self.doc_ids.index(doc_id)
            documents.append(self.doc_texts[idx])
            metadatas.append(self.doc_metadatas[idx])
            distances.append(1 - combined_scores[doc_id]["combined"])  # Convert back to distance-like
        
        return {
            "ids": [top_ids],
            "documents": [documents],
            "metadatas": [metadatas],
            "distances": [distances]
        }

if __name__ == "__main__":
    # Test
    model = get_embedding_model()
    chroma_client = PersistentClient(path="./chroma_db")
    collection = chroma_client.get_collection("professor_reviews")
    
    searcher = HybridSearcher(collection, model, alpha=0.5)
    
    test_queries = [
        "Which professor teaches CISC 3130?",
        "What do students say about Professor Levitan?",
        "What do students say about Professor Gross?"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"QUERY: {query}")
        print(f"{'='*60}")
        
        results = searcher.search(query, n_results=3)
        
        for i, doc in enumerate(results["documents"][0]):
            source = results["metadatas"][0][i]["source_file"]
            print(f"\nResult {i+1}: {source}")
            print(f"Text: {doc[:200]}...")