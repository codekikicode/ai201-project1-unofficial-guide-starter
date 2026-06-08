import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv()

from embed import get_embedding_model, query_vector_store
from rag import generate_answer, get_groq_client
from chromadb import PersistentClient

st.title("The Unofficial Guide: Brooklyn College CS Professor Reviews")
st.write("Ask questions about CS professors based on student reviews.")

@st.cache_resource
def init():
    client = get_groq_client()
    model = get_embedding_model()
    chroma_client = PersistentClient(path="./chroma_db")
    collection = chroma_client.get_collection("professor_reviews")
    return client, model, collection

client, model, collection = init()

query = st.text_input("Your question:", placeholder="e.g., Which professor is best for data structures?")

if query:
    with st.spinner("Searching reviews..."):
        results = query_vector_store(query, collection, model, n_results=5)
        answer, sources = generate_answer(query, results, client)
    
    st.subheader("Answer")
    st.write(answer)
    
    st.subheader("Sources")
    for source in sources:
        st.write(f"- {source}")