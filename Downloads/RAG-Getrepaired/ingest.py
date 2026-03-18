import os
## Lets Python talk to your operating system — reading files, accessing environment variables.

from dotenv import load_dotenv
## Your API key is sitting in .env. This line gives Python the ability to read that file and load the key into memory. 
## Without this, Python has no idea your .env exists.

from sentence_transformers import SentenceTransformer
## This is the tool that converts text into vectors (numbers). 
## When you write "how are shops verified?" — this converts that sentence into something like [0.23, -0.87, 0.45, ...] 
## — 384 numbers that represent the meaning of that sentence.

import chromadb
## This is your vector database. Think of it like a special Excel sheet that stores those 384 numbers per chunk 
## — and can instantly find which rows are most similar to a new question.

load_dotenv()  ## load .env file in the memory

model = SentenceTransformer('all-MiniLM-L6-v2') ## load the embedding model

client = chromadb.PersistentClient(path="./chroma_db") ## create persistent local database

collection = client.get_or_create_collection(name = 'getrepaired') ## create or load collection

with open('data/getrepaired_faq.txt',"r") as f: ## open the FAQ file
     text = f.read() ## read the entire content as string

chunks = [c.strip() for c in text.split("\n\n")if c.strip()]  ## # split by blank line into chunks


### generate embeddings and store in ChromaDB
embeddings = model.encode(chunks).tolist() ## Take every chunk of text 
## → convert each one into 384 numbers 
## → store all of them in a list. This is the "meaning" of each chunk in number form.
collection.upsert(
    documents = chunks,   # original text
    embeddings = embeddings,  # vector representation
    ids=[f"chunk_{i}" for i in range(len(chunks))]  # unique id for each chunk — upsert updates if exists, adds if new
)
print(f"Ingested {len(chunks)} chunks into ChromaDB")  # confirm success