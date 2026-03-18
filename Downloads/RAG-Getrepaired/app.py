import streamlit as st  # ui framework

st.set_page_config(
    page_title="Get Repaired AI Assistant",
    page_icon="🔧",
    layout="centered"
)

# ── Brand CSS ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Page background */
    .stApp {
        background-color: #f0f4f8;
    }

    /* Header banner */
    .header-banner {
        background-color: #1560BD;
        padding: 24px 32px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        gap: 20px;
        margin-bottom: 24px;
    }
    .header-text h1 {
        color: white;
        font-size: 28px;
        margin: 0;
        font-weight: 700;
    }
    .header-text p {
        color: #d0e4ff;
        font-size: 14px;
        margin: 4px 0 0 0;
    }

    /* Input box */
    .stTextInput > div > div > input {
        border: 2px solid #1560BD;
        border-radius: 8px;
        padding: 12px;
        font-size: 15px;
        background-color: white;
    }
    .stTextInput > div > div > input:focus {
        border-color: #3DB84B;
        box-shadow: 0 0 0 2px rgba(61,184,75,0.2);
    }

    /* Answer box */
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

    /* Footer */
    .footer {
        text-align: center;
        color: #888;
        font-size: 12px;
        margin-top: 40px;
        padding-top: 16px;
        border-top: 1px solid #dde3ec;
    }

    /* Hide streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ── Auto Ingest on startup ──────────────────────────────────────────────────────
@st.cache_resource  # runs only once per session
def run_ingest():
    import os
    from dotenv import load_dotenv
    from sentence_transformers import SentenceTransformer
    import chromadb

    load_dotenv()
    model = SentenceTransformer('all-MiniLM-L6-v2')
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_or_create_collection(name="getrepaired")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    faq_path = os.path.join(base_dir, "data", "getrepaired_faq.txt")
    with open(faq_path, "r") as f:
        text = f.read()

    chunks = [c.strip() for c in text.split("\n\n") if c.strip()]
    embeddings = model.encode(chunks).tolist()
    collection.upsert(
        documents=chunks,
        embeddings=embeddings,
        ids=[f"chunk_{i}" for i in range(len(chunks))]
    )
    return True

run_ingest()  # always runs on startup — safe because upsert handles duplicates

# ── Load RAG ───────────────────────────────────────────────────────────────────
@st.cache_resource  # load model only once
def load_rag():
    from query import query_rag  # import inside function to avoid blocking UI
    return query_rag

query_rag = load_rag()

# ── Header ─────────────────────────────────────────────────────────────────────
col1, col2 = st.columns([1, 4])
with col1:
    import os
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

# ── Input ──────────────────────────────────────────────────────────────────────
question = st.text_input(
    "Ask anything about Get Repaired:",
    placeholder="e.g. How are repair shops verified?"
)

# ── Answer ─────────────────────────────────────────────────────────────────────
if question:
    with st.spinner("Finding the best answer for you..."):
        answer = query_rag(question)

    st.markdown(f"""
    <div class="answer-box">
        <strong style="color: #1560BD;">Answer:</strong><br><br>
        {answer}
    </div>
    """, unsafe_allow_html=True)

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
    © 2026 Get Repaired · AI Assistant · Built with RAG Pipeline
</div>
""", unsafe_allow_html=True)
