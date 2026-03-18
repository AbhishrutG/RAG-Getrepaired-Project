# Get Repaired AI Assistant — RAG Pipeline

A production-ready AI chatbot built for **GetRepaired.de** using RAG (Retrieval-Augmented Generation) architecture.
The chatbot answers questions about the Get Repaired platform by reading from a knowledge base — not from general internet knowledge.

---

## What is RAG?

RAG stands for **Retrieval-Augmented Generation**.

In simple terms:
- You give the AI a **document** (your knowledge base)
- When a user asks a question, the AI **searches that document** for the most relevant parts
- It then uses those parts to **generate a proper answer**

This is different from a normal AI chatbot that answers from its general training data.
RAG makes the AI answer **only from your specific documents** — making it accurate and trustworthy for your business.

---

## How This Pipeline Works

```
User Question
     ↓
Convert question to numbers (vector) using SentenceTransformer
     ↓
Search ChromaDB for the 3 most similar chunks from the FAQ
     ↓
Send question + those 3 chunks to Groq (LLaMA 3.1)
     ↓
LLaMA generates a human-readable answer based on those chunks
     ↓
Answer displayed to user in Streamlit UI
```

---

## Project Structure

```
RAG-Getrepaired/
│
├── data/
│   └── getrepaired_faq.txt     ← The knowledge base (FAQ documents)
│
├── ingest.py                   ← Reads FAQ → converts to vectors → stores in ChromaDB
├── query.py                    ← Takes question → searches ChromaDB → sends to Groq → returns answer
├── app.py                      ← Streamlit web UI with Get Repaired branding
│
├── .env                        ← Your API keys (never committed to GitHub)
├── .gitignore                  ← Ignores .env and chroma_db folder
└── README.md                   ← This file
```

---

## File Explanations

### `data/getrepaired_faq.txt`
This is the **brain of the chatbot**. It contains all the questions and answers about the Get Repaired platform — how it works, how shops are verified, pricing, cities, warranty, etc.

Each Q&A is separated by a blank line. When `ingest.py` runs, it splits this file by blank lines to create individual **chunks**.

---

### `ingest.py`
This is the **teacher** — it teaches the database what the documents mean.

What it does step by step:
1. Opens `getrepaired_faq.txt` and reads the entire content
2. Splits the content into chunks (one Q&A = one chunk)
3. Converts each chunk into 384 numbers (called a **vector**) using `SentenceTransformer`
4. Stores those numbers + original text into **ChromaDB** (vector database)

> Run this file whenever you update the FAQ. Uses `upsert` so you never need to delete the database.

---

### `query.py`
This is the **search + answer engine**.

What it does step by step:
1. Takes the user's question as input
2. Converts the question into 384 numbers (same model as ingest.py)
3. Asks ChromaDB — *"which stored chunks are closest to this question's numbers?"*
4. Gets back the top 3 most relevant FAQ chunks
5. Sends those 3 chunks + the original question to **Groq (LLaMA 3.1)**
6. LLaMA reads the chunks and writes a proper answer
7. Returns the answer

---

### `app.py`
This is the **user interface** built with Streamlit.

- Displays the Get Repaired logo and brand colors (blue `#1560BD`, green `#3DB84B`)
- Has a text input box for the user to ask questions
- Shows a loading spinner while fetching the answer
- Displays the answer in a styled box
- Includes suggested questions for quick access

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.12 | Programming language |
| SentenceTransformers (`all-MiniLM-L6-v2`) | Converts text to vectors (384 dimensions) |
| ChromaDB | Vector database — stores and searches vectors |
| Groq API | Runs LLaMA 3.1 model to generate answers |
| Streamlit | Web UI framework |
| python-dotenv | Loads API keys from `.env` file |

---

## What is a Vector?

Every piece of text gets converted into **384 numbers**.
These numbers represent the **meaning** of that text — not just the words.

Example:
- *"How are shops verified?"* → `[0.23, -0.87, 0.45, ...]` (384 numbers)
- *"What is the shop vetting process?"* → `[0.21, -0.85, 0.44, ...]` (very similar numbers)

ChromaDB finds similarity between vectors using **cosine similarity** — it measures how close two sets of numbers are. Closer = more relevant.

---

## Setup Instructions

### 1. Create conda environment
```bash
conda create -n rag-getrepaired python=3.12 -y
conda activate rag-getrepaired
```

### 2. Install dependencies
```bash
pip install sentence-transformers chromadb groq streamlit python-dotenv
```

### 3. Create `.env` file
```
GROQ_API_KEY=your_groq_api_key_here
```
Get your free API key at: [console.groq.com](https://console.groq.com)

### 4. Ingest the knowledge base
```bash
python ingest.py
```
Expected output: `Ingested 24 chunks into ChromaDB`

### 5. Test the query engine
```bash
python query.py
```
Type a question when prompted.

### 6. Run the Streamlit app
```bash
streamlit run app.py
```
Opens at: `http://localhost:8501`

---

## How to Add New Content

1. Open `data/getrepaired_faq.txt`
2. Add new Q&A at the bottom (separated by a blank line)
3. Run `python ingest.py` again

No need to delete the database — `upsert` handles duplicates automatically.

---

## Important Notes

- **Never commit `.env`** — it contains your API key. It is already in `.gitignore`.
- **Never commit `chroma_db/`** — it is auto-generated when you run `ingest.py`. It is already in `.gitignore`.
- The embedding model (`all-MiniLM-L6-v2`) downloads automatically on first run (~90MB).

---

## Built For

**GetRepaired.de** — A repair marketplace connecting customers with verified local repair shops across Germany and India.

> *This RAG pipeline is portfolio-ready and production-ready. It can be deployed to any cloud server and connected to a live database for real-time knowledge updates.*

---

## Author

**Abhishrut Giradkar**
AI Automation Engineer
[LinkedIn](https://linkedin.com/in/abhishrutgiradkar) · [GitHub](https://github.com/AbhishrutG)
