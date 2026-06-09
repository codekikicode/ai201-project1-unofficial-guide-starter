from chunk import chunk_all_documents
from ingest import load_documents

docs = load_documents()
chunks = chunk_all_documents(docs)

print(f"Total chunks: {len(chunks)}\n")

for i, chunk in enumerate(chunks[:5]):
    print(f"--- {chunk['id']} ---")
    print(f"Source: {chunk['metadata']['source_file']}")
    print(f"Text: {chunk['text'][:300]}...")
    print()