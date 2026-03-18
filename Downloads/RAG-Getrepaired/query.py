import os  ## access enviroment variables
from dotenv import load_dotenv  ## load env file
from sentence_transformers import SentenceTransformer ## convert question to vector
import chromadb ## vector database
from groq import Groq ##LLM to generate answers

load_dotenv() ## load .env file
model = SentenceTransformer('all-MiniLM-L6-v2')  # same embedding model as ingest.py
client = chromadb.PersistentClient(path="./chroma_db")  # connect to existing database
collection = client.get_or_create_collection(name="getrepaired")  # load existing collection
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))  # connect to Groq LLM


def query_rag(question):  # takes user question as input
    
    question_embedding = model.encode(question).tolist()  # convert question to vector
    
    results = collection.query(
        query_embeddings=[question_embedding],  # search using the vector
        n_results=3  # return top 3 most relevant chunks
    )
    
    context = "\n\n".join(results['documents'][0])  # join the 3 chunks into one block of text
    response = groq_client.chat.completions.create(
       model="llama-3.1-8b-instant",  # LLaMA 3 model on Groq
        messages=[
            {"role": "system", "content": "You are a helpful assistant for Get Repaired platform. Answer only based on the context provided."},  # tells LLM who it is
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}  # sends chunks + question
        ]
    )
    
    return response.choices[0].message.content  # return the generated answer

if __name__ == "__main__":  # only runs when you execute this file directly
    question = input("Ask a question: ")  # take question from user
    answer = query_rag(question)  # get answer
    print(f"\nAnswer: {answer}")  # print the answer