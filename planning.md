# Project 1 Planning: The Unofficial Guide

---

## Domain

The domain I chose was Brooklyn College Computer Science Professor Reviews. This knowledge is valuable because CISC students need to know which professors make the effort to explain programming concepts clearly, grade fairly, and overall create a supportive classroom environment. The information is drawn from informal student reviews on Rate My Professors, Coursicle, and Reddit threads. The Computer Information Science course catalog on the official Brooklyn College site only lists department faculty,  department location, and course descriptions -- not teaching quality or overall student experience.

---

## Documents

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Rate My Professors | Professor Amara Auguste (CISC 1115)| https://www.ratemyprofessors.com/professor/2950851 |
| 2 | Rate My Professors | Professor Carlos Cuevas, review 1 (CISC 3810) | https://www.ratemyprofessors.com/professor/2974235 |
| 3 | Rate My Professors | Professor Carlos Cuevas, review 2 (CISC 3810) | https://www.ratemyprofessors.com/professor/2974235 |
| 4 | Rate My Professors | Professor Murray Gross (CISC 3140) | https://www.ratemyprofessors.com/professor/167158 |
| 5 | Rate My Professors | Professor Priyanka Samanta, review 1 (CISC 1050) | https://www.ratemyprofessors.com/professor/2757901 |
| 6 | Rate My Professors | Professor Priyanka Samanta, review 2 (CISC 3140) | https://www.ratemyprofessors.com/professor/2757901 |
| 7 | Rate My Professors | Professor Neng-Fa Zhou (CISC 3160) | https://www.ratemyprofessors.com/professor/176933 |
| 8 | Coursicle | Professor Rivka Levitan (CISC 3130, CISC 3320) | https://www.coursicle.com/brooklyncuny/?professor=Rivka+Levitan&type=reviews |
| 9 | Reddit| r/BrooklynCollege "How is the CS program?" | https://www.reddit.com/r/BrooklynCollege/comments/kgppkf/how_is_the_cs_program/ |
| 10 |Reddit | r/BrooklynCollege CS program facilities comment | https://www.reddit.com/r/BrooklynCollege/comments/kgppkf/how_is_the_cs_program/ |

---

## Chunking Strategy

**Chunk size:** 500 characters

**Overlap:** 100 characters

**Reasoning:** My documents are mostly short reviews (1-3 paragraphs) and Reddit comments. 500 characters captures most complete reviews in a single chunk, while overlap ensures that if a key fact spans the boundary between two chunks, both chunks retain enough context to be meaningful. For example, a review mentioning both 'Data Structures' and 'explains clearly' won't get split awkwardly. 

If chunks were too small (200 chars), reviews would get fragmented and lose meaning. If too large (1000+ chars), multiple reviews might merge into one chunk, making retrieval less precise.

---

## Retrieval Approach

**Embedding model:** all-MiniLM-L6-v2 via sentence-transformers. This model is lightweight (80MB), fast, and works well for semantic similarity on short English text.

**Top-k:**  I retrieve top-5 chunks per query. Top-5 gives the LLM enough context without overwhelming it with irrelevant chunks -- too few (1-2) and it might miss important perspectives, too many (10+) and the model introduces noise and increases token cost. 

**Production tradeoff reflection:** For production, I'd strongly consider: larger models like all-mpnet-base-v2 for better accuracy, OpenAI's text-embedding-3-small for multilingual support, or domain-specific fine-tuned models for more detailed professor review data. 

---

## Evaluation Plan

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | "Which professor teaches CISC 3130 -- Data Structures?" | "Professor Rivka Levitan teaches CISC 3130 -- Data Structures" |
| 2 | "What do students say about Professor Levitan's teaching style?" | "Students say she is knowledgeable, has a nice voice, explains things clearly, and her class is stress-free." |
| 3 | "What do students say about Professor Zhou's teaching style?" | "Students say Professor Zhou is a nice person but his lectures can be boring. They advise not relying on lectures and studying outside of class. He can be a tough grader on exams but may boost final grades. He is accessible during office hours." |
| 4 | "What complaints do students have about the Brooklyn College program facilities?" | "Students complain about roaches, dirty walls, broken chalkboards, holes in walls, non-working clocks, and overcrowded classrooms with more students than chairs. There was a protest after a ceiling caved in." |
| 5 | "What do students say about Professor Gross?" | "Students describe him as the worst professor in 6 years, with no Brightspace, no lectures or grades posted, exams graded his way or no credit, waste-of-time lectures, an ego, and yelling at students. He didn't curve and students got D+ grades despite getting B or above in other CS classes." |

---

## Anticipated Challenges

1. Inconsistent review quality and structure: Some reviews are very short (Samanta's "She is good overall, but the labs were a headache") while others are detailed narratives (Gross's multi-sentence complaint). Short reviews provide less semantic signal for embedding, making them harder to retrieve accurately. The chunking strategy must handle both without losing the short ones entirely or fragmenting the long ones awkwardly. 

2. Missing source attribution and cross-document blending: The LLM might generate an answer that mixes facts from multiple professors without clearly citing which document each came from. For example, saying "Professor Cuevas explains things clearly" when that actually came from Levitan's review. I addressed this by explicitly prompting the model to cite sources and including source metadata in every chunk, but the model still occasionally paraphrases without clear attribution.

3. Off-topic retrieval for comparative questions: Questions like "Which professor has the highest rating?" require comparing numerical values across multiple documents. Semantic search retrieves chunks that are similar to the query, not chunks that contain the highest value. The system might retrieve a professor with a 3.0 rating instead of a 5.0 rating because the 3.0 review contains more text about "ratings" in general. This is a fundamental limitation of pure semantic retrieval for aggregation queries. 

4. Reddit noise and mixed topics: The Reddit documents contain multiple comments with different topics (facilities, course availability, professor quality). A query about "facilities" might retrieve a chunk that also mentions professors, or vice versa, because the comments are concatenated in the same file. I mitigated this by splitting the two major Reddit comments into separate files, but I know that shorter interweaved commentary can still create noise.

---

## Architecture

┌─────────────────┐        ┌─────────────┐       ┌─────────────────────────┐
│  10 .txt files  │────▶  │  26 chunks   │────▶ │  all-MiniLM-L6-v2       │
│  in documents/  │        │  500 chars  │       │  sentence-transformers  │
│                 │        │ 100 overlap │       │                         │
└─────────────────┘        └─────────────┘       └─────────────────────────┘
Ingestion                  Chunking               Embedding
(ingest.py)                (chunk.py)             (embed.py)
┌─────────────────────────┐      ┌─────────────────────────┐
│      ChromaDB           │────▶│   BM25 + Semantic       │
│   vector database       │      │   Hybrid Search        │
│   cosine similarity     │      │   rank-bm25 library    │
│   top-5 retrieval       │      │   alpha=0.5 combined   │
└─────────────────────────┘      └────────────────────────┘
Retrieval                        Re-ranking
(embed.py)                       (hybrid_search.py)
┌─────────────────────────┐
│    Groq LLM             │
│  llama-3.1-8b-instant   │
│   grounded generation   │
│   with source citation  │
└─────────────────────────┘
Generation
(rag.py)

---

## AI Tool Plan

I used AI (v. 2.6 Kimi) to help implement the chunking strategy and retrieval pipeline. I provided my chunking strategy section and asked for a Python implementation of the chunk_text() function with sentence-boundary awareness. I also used the chat to debug the Groq API integration when the model was decommissioned, and to structure the Streamlit interface.

**Milestone 3 — Ingestion and chunking:**
- I gave Kimi my chunking strategy parameters (500 characters, 100 overlap, sentence-boundary awareness, short review documents) and asked for a Python implementation.
- Kimi returned a basic character-splitting function. I revised it to add sentence-boundary detection (searching the last 50 characters for periods/newlines) and a minimum-content threshold to prevent tiny fragments.
- I also used Kimi to debug file loading issues when `mkdir documents` failed because the directory already existed.

**Milestone 4 — Embedding and retrieval:**
- I asked Kimi to implement the ChromaDB vector store setup and embedding pipeline using `sentence-transformers` and `all-MiniLM-L6-v2`.
- Kimi provided the initial code, but I had to add `load_dotenv()` to fix the Groq API key loading issue that caused a `ValueError` on startup.
- For the stretch challenge, I asked Kimi to help implement BM25 hybrid search. Kimi suggested the `rank-bm25` library and provided the scoring combination logic. I adjusted the alpha weighting (0.5) after testing.

**Milestone 5 — Generation and interface:**
- I used Kimi to structure the Streamlit interface (`app.py`) after the CLI version was working.
- Kimi also helped debug the Groq model decommissioning error (`llama3-8b-8192` → `llama-3.1-8b-instant`) and suggested the system prompt design for grounded generation with source citation.

---

## Stretch Challenge: Hybrid Search

I implemented hybrid search combining semantic search (all-MiniLM-L6-v2 embeddings) with BM25 keyword search to address the failure case where "Professor Levitan" without "Rivka" returned no results.

**Why hybrid search:** The failure occurred because the embedding model didn't associate "Levitan" with the review content (the name was in the header, but reviews used "she/her"). BM25 keyword search finds exact word matches regardless of semantic context.

**Implementation:** I added `rank-bm25` library, tokenized documents and queries, and combined scores with alpha=0.5 (equal weight to semantic and BM25).

**Result:** The same query ("What do students say about Professor Levitan?") now correctly retrieves `coursicle_levitan.txt` and generates a detailed, cited answer.

**Tradeoff:** Hybrid search adds latency (BM25 index building) and complexity, but significantly improves recall for name-based queries.

---