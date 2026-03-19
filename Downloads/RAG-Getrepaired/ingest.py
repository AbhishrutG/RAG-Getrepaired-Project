import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import chromadb

load_dotenv()

# ── Step 1: Smart Chunking with Overlap ───────────────────────────────────────
def chunk_text(text, chunk_size=500, overlap=100):
    """Split text into overlapping chunks so no context is lost at boundaries"""
    chunks = []
    sentences = text.replace('\n', ' ').split('. ')
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) < chunk_size:
            current_chunk += sentence + ". "
        else:
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
            # overlap: carry last N words into next chunk
            words = current_chunk.split()
            overlap_text = " ".join(words[-20:]) if len(words) > 20 else current_chunk
            current_chunk = overlap_text + " " + sentence + ". "

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks

# ── Step 2: Load Multiple File Types ─────────────────────────────────────────
def load_documents(data_dir="data"):
    """Load all .txt and .pdf files from data directory"""
    all_text = ""

    for filename in os.listdir(data_dir):
        if filename in ["logo.jpeg", "logo.png"]:
            continue  # skip image files

        filepath = os.path.join(data_dir, filename)

        if filename.endswith(".txt"):
            with open(filepath, "r", encoding="utf-8") as f:
                all_text += f.read() + "\n\n"
            print(f"Loaded: {filename}")

        elif filename.endswith(".pdf"):
            try:
                import pypdf
                reader = pypdf.PdfReader(filepath)
                for page in reader.pages:
                    all_text += page.extract_text() + "\n\n"
                print(f"Loaded PDF: {filename}")
            except ImportError:
                print(f"pypdf not installed, skipping {filename}")
            except Exception as e:
                print(f"Error loading {filename}: {e}")

    return all_text

# ── Step 3: Initialize Models and DB ─────────────────────────────────────────
model = SentenceTransformer('all-MiniLM-L6-v2')
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="getrepaired")

# ── Step 4: Load, Chunk, Embed, Store ────────────────────────────────────────
text = load_documents()
chunks = chunk_text(text)
embeddings = model.encode(chunks).tolist()

collection.upsert(
    documents=chunks,
    embeddings=embeddings,
    ids=[f"chunk_{i}" for i in range(len(chunks))]
)

print(f"Ingested {len(chunks)} chunks into ChromaDB")
