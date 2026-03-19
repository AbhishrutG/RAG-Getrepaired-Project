import os
import streamlit as st

st.set_page_config(
    page_title="Get Repaired AI Assistant",
    page_icon="https://raw.githubusercontent.com/AbhishrutG/RAG-Getrepaired-Project/main/data/logo.jpeg",
    layout="centered"
)

# ── Brand CSS ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #f0f4f8; }

    .stTextInput > div > div > input {
        border: 2px solid #1560BD;
        border-radius: 8px;
        padding: 12px;
        font-size: 15px;
        background-color: white;
        color: #111111 !important;
        caret-color: #1560BD !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #3DB84B;
        box-shadow: 0 0 0 2px rgba(61,184,75,0.2);
    }

    .answer-box {
        background-color: white;
        border-left: 5px solid #3DB84B;
        border-radius: 8px;
        padding: 20px 24px;
        margin-top: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        font-size: 15px;
        line-height: 1.7;
        color: #1a1a2e;
    }

    .rewrite-box {
        background-color: #eef4ff;
        border-left: 4px solid #1560BD;
        border-radius: 6px;
        padding: 10px 16px;
        margin-top: 12px;
        font-size: 13px;
        color: #1560BD;
    }

    .chat-user {
        background-color: #1560BD;
        color: white;
        border-radius: 12px 12px 2px 12px;
        padding: 12px 16px;
        margin: 8px 0;
        max-width: 80%;
        margin-left: auto;
        font-size: 14px;
    }

    .chat-bot {
        background-color: white;
        border: 1px solid #dde3ec;
        border-radius: 12px 12px 12px 2px;
        padding: 12px 16px;
        margin: 8px 0;
        max-width: 80%;
        font-size: 14px;
        color: #1a1a2e;
        line-height: 1.6;
    }

    .footer {
        text-align: center;
        color: #888;
        font-size: 12px;
        margin-top: 40px;
        padding-top: 16px;
        border-top: 1px solid #dde3ec;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ── Auto Ingest on startup ─────────────────────────────────────────────────────
@st.cache_resource
def run_ingest():
    from dotenv import load_dotenv
    from sentence_transformers import SentenceTransformer
    import chromadb

    load_dotenv()
    model = SentenceTransformer('all-MiniLM-L6-v2')
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_or_create_collection(name="getrepaired")

    base_dir = os.path.dirname(os.path.abspath(__file__))

    def chunk_text(text, chunk_size=500, overlap=100):
        chunks = []
        sentences = text.replace('\n', ' ').split('. ')
        current_chunk = ""
        for sentence in sentences:
            if len(current_chunk) + len(sentence) < chunk_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                words = current_chunk.split()
                overlap_text = " ".join(words[-20:]) if len(words) > 20 else current_chunk
                current_chunk = overlap_text + " " + sentence + ". "
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        return chunks

    faq_path = os.path.join(base_dir, "data", "getrepaired_faq.txt")
    with open(faq_path, "r") as f:
        text = f.read()

    chunks = chunk_text(text)
    embeddings = model.encode(chunks).tolist()
    collection.upsert(
        documents=chunks,
        embeddings=embeddings,
        ids=[f"chunk_{i}" for i in range(len(chunks))]
    )
    return True

run_ingest()

# ── Load RAG ───────────────────────────────────────────────────────────────────
@st.cache_resource
def load_rag():
    from query import query_rag
    return query_rag

query_rag = load_rag()

# ── Session State ──────────────────────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []       # for Groq LLM memory
if "messages" not in st.session_state:
    st.session_state.messages = []           # for chat UI display

# ── Header ─────────────────────────────────────────────────────────────────────
col1, col2 = st.columns([1, 4])
with col1:
    logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "logo.jpeg")
    st.image(logo_path, width=90)
with col2:
    st.markdown("""
    <div style="padding-top: 10px;">
        <h1 style="color: #1560BD; margin: 0; font-size: 26px;">Get Repaired AI Assistant</h1>
        <p style="color: #555; margin: 4px 0 0 0; font-size: 14px;">WE COME TO YOU &nbsp;|&nbsp; Powered by AI</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ── Chat History Display ───────────────────────────────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="chat-user">🙋 {msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-bot">🤖 {msg["content"]}</div>', unsafe_allow_html=True)

# ── Input ──────────────────────────────────────────────────────────────────────
question = st.text_input(
    "Ask anything about Get Repaired:",
    placeholder="e.g. How are repair shops verified?",
    key="input"
)

# ── Answer ─────────────────────────────────────────────────────────────────────
if question:
    with st.spinner("Thinking..."):
        answer, sources, rewritten_query = query_rag(question, st.session_state.chat_history)

    # Update LLM memory
    st.session_state.chat_history.append({"role": "user", "content": question})
    st.session_state.chat_history.append({"role": "assistant", "content": answer})
    if len(st.session_state.chat_history) > 10:
        st.session_state.chat_history = st.session_state.chat_history[-10:]

    # Update chat UI
    st.session_state.messages.append({"role": "user", "content": question})
    st.session_state.messages.append({"role": "assistant", "content": answer})

    # Show rewritten query
    if rewritten_query.lower() != question.lower():
        st.markdown(f'<div class="rewrite-box">🔍 <strong>Searched as:</strong> {rewritten_query}</div>', unsafe_allow_html=True)

    # Show answer
    st.markdown(f"""
    <div class="answer-box">
        <strong style="color: #1560BD;">Answer:</strong><br><br>
        {answer}
    </div>
    """, unsafe_allow_html=True)

    # Show sources
    with st.expander("📄 Sources used to generate this answer"):
        for i, source in enumerate(sources):
            st.markdown(f"**Source {i+1}:**")
            st.info(source[:300] + "..." if len(source) > 300 else source)

    # Clear button
    if st.button("🗑️ Clear conversation"):
        st.session_state.chat_history = []
        st.session_state.messages = []
        st.rerun()

# ── Suggested Questions ────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("**Suggested questions:**")
col1, col2 = st.columns(2)
with col1:
    st.markdown("- How are repair shops verified?")
    st.markdown("- What happens if repair goes wrong?")
    st.markdown("- Which cities does Get Repaired operate in?")
with col2:
    st.markdown("- How does pricing work?")
    st.markdown("- How do I track my repair?")
    st.markdown("- How long does a repair take?")

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    © 2026 Get Repaired · AI Assistant · RAG Pipeline with Memory, Hybrid Search & Re-ranking
</div>
""", unsafe_allow_html=True)
