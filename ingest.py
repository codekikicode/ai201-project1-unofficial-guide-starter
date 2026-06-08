import os
import re

def load_documents(documents_dir="documents"):
    """Load all text files from the documents directory."""
    documents = []
    for filename in os.listdir(documents_dir):
        if filename.endswith(".txt"):
            filepath = os.path.join(documents_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
            
            # Clean the text
            text = clean_text(text)
            
            documents.append({
                "id": filename,
                "text": text,
                "source": filepath
            })
    return documents

def clean_text(text):
    """Remove extra whitespace, normalize line breaks."""
    # Remove extra blank lines
    text = re.sub(r'\n\s*\n', '\n\n', text)
    # Remove leading/trailing whitespace
    text = text.strip()
    return text

if __name__ == "__main__":
    docs = load_documents()
    print(f"Loaded {len(docs)} documents")
    for doc in docs:
        print(f"  {doc['id']}: {len(doc['text'])} chars")