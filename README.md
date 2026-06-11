# The Unofficial Guide — Project 1

---

## Domain

The domain I chose was Brooklyn College Computer Science Professor Reviews. This knowledge is valuable because CISC students need to know which professors make the effort to explain programming concepts clearly, grade fairly, and overall create a supportive classroom environment. The information is drawn from informal student reviews on Rate My Professors, Coursicle, and Reddit threads. The Computer Information Science course catalog on the official Brooklyn College site only lists department faculty,  department location, and course descriptions -- not teaching quality or overall student experience.

---

## Document Sources

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Rate My Professors |  Professor Amara Auguste (CISC 1115)| https://www.ratemyprofessors.com/professor/2950851 |
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

**Why these choices fit your documents:** My documents are mostly short reviews (1-3 paragraphs) and Reddit comments. 500 characters captures most complete reviews in a single chunk, while overlap ensures that if a key fact spans the boundary between two chunks, both chunks retain enough context to be meaningful. For example, a review mentioning both 'Data Structures' and 'explains clearly' won't get split awkwardly. If the chunks were too small (200 chars), reviews would get fragmented and lose meaning. If too large (1000+ chars), multiple reviews might merge into one chunk, making retrieval less precise.

**Preprocessing:** Before chunking, I cleaned each document by removing unnecessary headers and footnotes, extra blank lines and stripping leading/trailing whitespace. This prevents empty or near-empty chunks from formatting artifacts.

**Final chunk count:** 26 chunks from 10 documents.

---

## Sample Chunks

| Chunk ID | Source Document | Text Preview |
|----------|-----------------|--------------|
| auguste_rmp.txt_chunk_0 | auguste_rmp.txt | Professor: Amara Auguste... Java is hard, but she makes it as easy as possible... |
| auguste_rmp.txt_chunk_1 | auguste_rmp.txt | odelab for easy points. She has her own website... |
| coursicle_levitan.txt_chunk_0 | coursicle_levitan.txt | Professor Rivka Levitan... CISC 3130 - Data Structures... |
| coursicle_levitan.txt_chunk_1 | coursicle_levitan.txt | stress free while also being very knowledgable... |
| coursicle_levitan.txt_chunk_2 | coursicle_levitan.txt | ctures. We had two exams and final... |

---

## Embedding Model

**Model used:** all-MiniLM-L6-v2 via sentence-transformers. This model is lightweight (80MB), fast, and works well for semantic similarity on short English text.

**Production tradeoff reflection:**

- Context length: all-MiniLM-L6-v2 handles 256 tokens max, which is fine for short reviews but would truncate longer documents. For production with mixed-length content (syllabi, long guides), I'd use models with 512+ token limits like all-mpnet-base-v2 or OpenAI's text-embedding-3-large.

- Multilingual support: My corpus is entirely English. If serving CUNY's diverse linguistic population, which often includes international students, I'd switch to OpenAI's text-embedding-3-small which handles 100+ languages, or a multilingual model like paraphrase-multilingual-MiniLM-L12-v2.

- Accuracy on domain-specific text: Professor reviews use informal slang ("TAKE HER!!!", "waste-of-time lectures"). A general model captures these okay, but a model fine-tuned on educational review data would better understand domain-specific sentiment and terminology.

- Latency: all-MiniLM-L6-v2 runs locally but offer better accuracy. For real-time chat, I'd keep local embedding and only use API for the LLM generation step.

- Local vs. API-hosted: Local models are free and private (student data stays on campus), but require GPU for batch processing. API-hosted models scale better and update automatically, but create vendor lock-in and ongoing costs. For a CUNY deployment, local might be preferred for data privacy.

---

## Grounded Generation

**System prompt grounding instruction:**
The model receives two layers of grounding constraints:

1. **System-level instruction** (applied to every conversation):
   > "You are a helpful assistant that answers questions based only on provided context. Always cite your sources."

2. **User-level prompt** (per-query, with explicit context formatting):
   > "You are a helpful assistant for Brooklyn College students. Answer the question using ONLY the provided context. Do not use outside knowledge. Always cite which document(s) your answer comes from."

The retrieved chunks are structurally formatted to reinforce the boundary between context and general knowledge:

[Document 1 from coursicle_levitan.txt]
{chunk text}

[Document 2 from cuevas_rmp.txt]
{chunk text}

**How source attribution is surfaced in the response:**
Source attribution is enforced at two levels:

1. **In the generated text** The model is instructed to cite which document each fact comes from (i.e., "According to Document 1 from cuevas_rmp.txt..."). The prompt explicitly demands this with "Always cite which document(s) your answer comes from."

2. **In the system output** The `generate_answer()` function returns `list(set(sources))` — a deduplicated list of all source files that contributed to the retrieved context. These are printed alongside the answer as `Sources: {', '.join(sources)}`.

There is no automatic filtering of low-relevance chunks; all top-5 retrieved chunks are passed to the LLM. The model is trusted to ignore irrelevant context due to the explicit grounding instruction and the low temperature (0.3) which reduces hallucination.

---

## Example Responses

**Response 1: Successful retrieval with source attribution**

**Query:** "Which professor teaches CISC 3130 -- Data Structures?"

**Answer:** According to Document 1 from coursicle_levitan.txt, Professor Rivka Levitan teaches CISC 3130 - Data Structures. The review states: "Easily the best CS professor ive had so far. Her class is stress free while also being very knowledgeable. She has a nice voice and explains things very clearly. TAKE HER!!! CISC 3130"

Sources: cuevas_rmp2.txt, coursicle_levitan.txt, samanta_rmp.txt, auguste_rmp.txt

**Response 2: Successful retrieval with source attribution**

**Query:** "What do students say about Professor Gross?"

**Answer:** According to Document 1 from gross_rmp.txt, students say that Professor Gross is the "worst professor" they have had in their 6 years at Brooklyn College. He does not use Brightspace, does not post lectures or grades, and has a tendency to yell at students in arguments. Additionally, he did not curve grades this semester.

Sources: cuevas_rmp2.txt, auguste_rmp.txt, cuevas_rmp.txt, samanta_rmp.txt, gross_rmp.txt

**Response 3: Out-of-scope query showing refusal**

**Query:** "What is the best restaurant near Brooklyn College?"

**Answer:** I don't have any information about restaurants near Brooklyn College in the provided context. The documents I have access to are about Brooklyn College Computer Science professors and program facilities.

Sources: reddit_cs_program_facilities.txt, reddit_cs_program.txt

---

## Query Interface

The system provides a simple command-line interface via `rag.py` and a web interface via `streamlit run app.py`.

**Input:** Plain text question (e.g., "Which professor is best for data structures?")

**Output:** 
- Generated answer with source citations
- List of source documents that contributed to the answer

**Sample interaction:**

**Query**: Which professor teaches CISC 3130 -- Data Structures?
**Response**: According to Document 1 from coursicle_levitan.txt, Professor Rivka Levitan teaches CISC 3130 - Data Structures...

Sources: cuevas_rmp2.txt, coursicle_levitan.txt, samanta_rmp.txt, auguste_rmp.txt

---

## Evaluation Report

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | "Which professor teaches CISC 3130 -- Data Structures?" | "Professor Rivka Levitan teaches CISC 3130 -- Data Structures" | Correctly identified Levitan, cited `coursicle_levitan.txt` with positive review quote. | **Relevant** -- Top result was the correct document with course listing. | **Accurate**  |
| 2 | "What do students say about Professor Levitan's teaching style?"| "Students say she is knowledgeable, has a nice voice, explains things clearly, and her class is stress-free." | System returned: "There is no information about Professor Levitan in the provided context." | **Off-Target** -- Retrieved unrelated documents (Zhou, Auguste, Cuevas, Samanta, Gross). Missed Levitan entirely. | **Inaccurate** -- Failure case: name-only query didn't match. |
| 3 | "What do students say about Professor Zhou's teaching style?" |  "Students say Professor Zhou is a nice person but his lectures can be boring. They advise not relying on lectures and studying outside of class. He can be a tough grader on exams but may boost final grades. He is accessible during office hours." | System returned reviews discussing boring lectures and independent study advice from `zhou_rmp.txt`. | **Relevant** -- Correct document was top result. | **Partially accurate** -- Captured main points but missed tough grader and office hours details. |
| 4 | "What complaints do students have about the Brooklyn College program facilities?" | "Students complain about roaches, dirty walls, broken chalkboards, holes in walls, non-working clocks, and overcrowded classrooms with more students than chairs. There was a protest after a ceiling caved in." | System returned comprehensive structured list of 7 complaints, all from `reddit_cs_program_facilities.txt`. | **Relevant** -- Correct document retrieved and fully utilized. | **Accurate** |
| 5 | "What do students say about Professor Gross?" | "Students describe him as the worst professor in 6 years, with no Brightspace, no lectures or grades posted, exams graded his way or no credit, waste-of-time lectures, an ego, and yelling at students. He didn't curve and students got D+ grades despite getting B or above in other CS classes." | System returned "Worst professor" review claim, no Brightspace usage claim, no lectures/grades claim, yelling, no curve from `gross_rmp.txt`. | **Relevant** -- Correct document in retrieved set | **Partially accurate** -- Core complaints captured, minor details (ego, waste-of-time) omitted. |

---

## Failure Case Analysis

**Question that failed:** Question 2: "What do students say about Professor Levitan's teaching style?"

**What the system returned:** "There is no information about Professor Levitan in the provided context."

**Root cause (tied to a specific pipeline stage):** The failure occurred at the **retrieval/embedding** stage. The query "Professor Levitan" without "Rivka" failed to match because the name "Rivka Levitan" appears in the document header/metadata, but the substantive review content uses pronouns ("she," "her," "ive"). The embedding model (all-MiniLM-L6-v2) did not create a strong semantic association between "Levitan" and the teaching style descriptions because the name and the review content were separated by chunk boundaries and metadata lines. 

The chunking strategy split the document such that the header (with the full name) and the review body (with the content) became separate chunks, and the embedding for the content chunks did not encode the professor's name. When the query was changed to "Professor Rivka Levitan," the system succeeded because the full name appeared in the header chunk, which was then retrieved.

**What you would change to fix it:** Add professor name as metadata to every chunk, or use a hybrid search (semantic + keyword) that boosts chunks containing the exact name.

---

## Retrieval Test Results

**Query 1: "Which professor teaches CISC 3130?"**

Top 3 retrieved chunks:
1. `coursicle_levitan.txt`: "Professor Rivka Levitan... CISC 3130 -- Data Structures..." -- **Relevant.** Directly lists the course number and professor name.
2. `samanta_rmp.txt`: "Professor: Priyanka Samanta... CISC1050..." -- **Less relevant.** Different professor, different course. Retrieved due to general professor/course similarity.
3. `coursicle_levitan.txt` (chunk 1): "stress free while also being very knowledgable..." -- **Partially relevant.** About the same professor but doesn't mention the course number.

**Query 2: "What do students say about Professor Gross?"**

Top 3 retrieved chunks:
1. `gross_rmp.txt`: "Professor: Murray Gross... worst professor... no Brightspace... yells at students..." -- **Highly relevant.** Directly answers the query with specific complaints.
2. `cuevas_rmp.txt`: "Professor: Carlos Cuevas... funny and kind..." -- **Irrelevant.** Different professor entirely. Retrieved due to general professor-review similarity.
3. `samanta_rmp.txt`: "Professor: Priyanka Samanta..." -- **Irrelevant.** Another different professor.

**Query 3: "What is the best restaurant near Brooklyn College?" (Out-of-scope)**

Top 3 retrieved chunks:
1. `reddit_cs_program_facilities.txt`: "Brooklyn College CS Program Review... roaches... dirty walls..." — **Irrelevant.** Mentions Brooklyn College but no restaurants.
2. `reddit_cs_program.txt`: "department pushes you with internship opportunities..." -- **Irrelevant.** General CS program discussion.
3. `reddit_cs_program.txt`: "Brooklyn College CS Program Review..." -- **Irrelevant.** No restaurant information.

For this out-of-scope query, no relevant chunks exist in the corpus. The system retrieved the closest semantic matches (documents mentioning Brooklyn College), but none contain restaurant information.

---

## Spec Reflection

**One way the spec helped you during implementation:** The structured milestones (documents → chunking → embedding → retrieval → generation) forced me to think about each pipeline stage separately. This prevented me from trying to build everything at once and getting overwhelmed. The chunking strategy section specifically made me consider why 500 characters made sense for short reviews rather than just picking a random number.

**One way your implementation diverged from the spec, and why:** The spec suggested collecting documents before writing any code, but I built the pipeline first and collected documents in parallel. This actually worked because I could test the pipeline with real data immediately, but it meant my chunking strategy was retrofitted rather than pre-planned. I also added a Streamlit interface even though the spec only required a basic query interface, because it made the demo video much clearer.

---

## AI Usage

**Instance 1: Implementing the chunking function**

- **What I gave the AI:** I provided my Chunking Strategy section from planning.md (500 characters, 100 overlap, sentence-boundary awareness, short review documents) and asked Kimi to implement a `chunk_text()` function.

- **What it produced:** Kimi returned a function using fixed character splitting with basic overlap, but it didn't handle sentence-boundary detection or the edge case where no period/newline exists within the search window.

- **What I changed/overrode:** I revised the function to add sentence-boundary awareness -- it now searches the last 50 characters of each chunk for a period or newline and breaks there if found. I also added a minimum-content threshold (break only if we have 80% of the chunk size) to prevent creating tiny fragments. This ensured reviews wouldn't get split mid-sentence.

**Instance 2: Debugging the Groq API model decommissioning**

- **What I gave the AI:** I pasted the error message `groq.BadRequestError: Error code: 400 - {'error': {'message': 'The model llama3-8b-8192 has been decommissioned...'}}` and asked Kimi for alternative models and how to update my code.

- **What it produced:** Kimi suggested three alternatives: `llama-3.1-8b-instant`, `llama-3.3-70b-versatile`, and `gemma2-9b-it`. It provided updated code with the new model name.

- **What I changed/overrode:** I selected `llama-3.1-8b-instant` instead of `llama-3.3-70b-versatile` because the larger model was unnecessary for short professor review answers and would increase token costs. I also kept the temperature at 0.3 (rather than Kimi's suggested 0.7) because grounded generation requires less creativity and more factual adherence.

**Instance 3: Implementing hybrid search for the stretch challenge**

- **What I gave the AI:** I described the failure case from my evaluation (Q2: "Professor Levitan" without "Rivka" returned no results) and asked Kimi how to combine semantic search with keyword/BM25 search to fix exact-name matching.

- **What it produced:** Kimi suggested the `rank-bm25` library and provided a `HybridSearcher` class that computes both semantic similarity (cosine distance via embeddings) and BM25 keyword scores, then combines them with weighted averaging.

- **What I changed/overrode:** I set `alpha=0.5` (equal weight to semantic and BM25) after testing. I also added a custom tokenizer that handles punctuation and lowercase normalization for better keyword matching. I simplified the score normalization because Kimi's initial version used complex min-max scaling that caused division-by-zero errors when all BM25 scores were zero.

---

## (Stretch Challenge): Hybrid Search

I compared semantic-only vs. hybrid search on 3 queries:

**Hybrid Search Comparison**

| Query | Semantic-Only Top Result | Hybrid Search Top Result | Winner |
|-------|-------------------------|-------------------------|--------|
| "Which professor teaches CISC 3130?" | `coursicle_levitan.txt` (correct) | `coursicle_levitan.txt` (correct) | Tie -- both work |
| "What do students say about Professor Levitan?" | `zhou_rmp.txt` (wrong — no Levitan info) | `coursicle_levitan.txt` (correct) | **Hybrid** -- fixed failure case |
| "What do students say about Professor Gross?" | `gross_rmp.txt` (correct) | `gross_rmp.txt` (correct) | Tie -- both work |

**Problem:** Pure semantic search failed when users asked about "Professor Levitan" without "Rivka" -- the embedding model didn't associate the surname with the review content.

**Solution:** `HybridSearcher` class computes both semantic similarity (cosine distance via embeddings) and BM25 keyword scores, then combines them with weighted averaging (alpha=0.5).

**Impact:** The failure case from the evaluation (Q2) is now resolved. The same query returns the correct document and a detailed, cited answer.

**Code:** `hybrid_search.py`

**Conclusion:** Hybrid search doesn't hurt queries that already work, but it fixes the exact-name matching failure. The BM25 component boosts chunks containing the exact surname, bridging the gap when embeddings miss name-to-content associations.

---