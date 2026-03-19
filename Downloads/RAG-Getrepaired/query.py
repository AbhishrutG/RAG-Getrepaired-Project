import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import chromadb
from groq import Groq

load_dotenv()

# ── Initialize ────────────────────────────────────────────────────────────────
model = SentenceTransformer('all-MiniLM-L6-v2')
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="getrepaired")
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ── Build BM25 Index from ChromaDB ────────────────────────────────────────────
def build_bm25_index():
    """Load all stored chunks and build a keyword search index"""
    try:
        from rank_bm25 import BM25Okapi
        all_docs = collection.get()
        if all_docs['documents']:
            tokenized = [doc.lower().split() for doc in all_docs['documents']]
            return BM25Okapi(tokenized), all_docs['documents']
    except ImportError:
        pass
    return None, []

bm25_index, all_chunks = build_bm25_index()

# ── Step 1: Query Rewriting ───────────────────────────────────────────────────
def rewrite_query(question):
    """Use LLM to make the question clearer and more searchable"""
    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "Rewrite the following question to be more specific and searchable for a device repair platform FAQ. Return only the rewritten question, nothing else."},
            {"role": "user", "content": question}
        ],
        max_tokens=80
    )
    return response.choices[0].message.content.strip()

# ── Step 2: Hybrid Search (Vector + BM25) ────────────────────────────────────
def hybrid_search(question, n_results=6):
    """Combine semantic vector search with keyword BM25 search"""
    # Vector search
    question_embedding = model.encode(question).tolist()
    vector_results = collection.query(
        query_embeddings=[question_embedding],
        n_results=n_results
    )
    vector_docs = vector_results['documents'][0]

    # BM25 keyword search
    if bm25_index and all_chunks:
        bm25_scores = bm25_index.get_scores(question.lower().split())
        top_indices = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)[:n_results]
        bm25_docs = [all_chunks[i] for i in top_indices if bm25_scores[i] > 0]

        # Combine both — deduplicated, vector results take priority
        combined = list(dict.fromkeys(vector_docs + bm25_docs))
        return combined[:n_results]

    return vector_docs

# ── Step 3: LLM Re-ranking ────────────────────────────────────────────────────
def rerank_chunks(question, chunks):
    """Use LLM to re-rank chunks by relevance to the question"""
    if len(chunks) <= 1:
        return chunks

    chunk_list = "\n\n".join([f"[{i+1}] {chunk[:200]}" for i, chunk in enumerate(chunks)])

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a relevance judge. Given a question and passages, return the numbers of the top 3 most relevant passages in order. Return ONLY numbers separated by commas. Example: 2,1,4"},
                {"role": "user", "content": f"Question: {question}\n\nPassages:\n{chunk_list}"}
            ],
            max_tokens=20
        )
        ranking_str = response.choices[0].message.content.strip()
        ranking = [int(x.strip()) - 1 for x in ranking_str.split(',') if x.strip().isdigit()]
        reranked = [chunks[i] for i in ranking if i < len(chunks)]

        # add any remaining chunks not in ranking
        for chunk in chunks:
            if chunk not in reranked:
                reranked.append(chunk)

        return reranked[:3]
    except Exception:
        return chunks[:3]  # fallback to original order

# ── Step 4: Main RAG Function ─────────────────────────────────────────────────
def query_rag(question, chat_history=[]):
    # Rewrite the question for better search
    rewritten_query = rewrite_query(question)

    # Hybrid search with rewritten query
    candidate_chunks = hybrid_search(rewritten_query, n_results=6)

    # Re-rank to get top 3 most relevant
    top_chunks = rerank_chunks(question, candidate_chunks)

    # Build context from top chunks
    context = "\n\n".join(top_chunks)

    # Generate answer with Groq
    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a helpful assistant for Get Repaired platform. Answer only based on the context provided. Remember previous messages in the conversation."},
            *chat_history,
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
        ]
    )

    answer = response.choices[0].message.content
    sources = top_chunks

    return answer, sources, rewritten_query

if __name__ == "__main__":
    question = input("Ask a question: ")
    answer, sources, rewritten = query_rag(question)
    print(f"\nRewritten query: {rewritten}")
    print(f"\nAnswer: {answer}")
    print(f"\nSources used: {len(sources)}")
