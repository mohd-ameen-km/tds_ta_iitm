import sqlite3
from sentence_transformers import SentenceTransformer
import os
from tqdm import tqdm

DB_PATH = "data/chunks.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS embeddings (
            chunk_id TEXT PRIMARY KEY,
            embedding BLOB
        )
    """)
    conn.commit()
    return conn

def fetch_chunks(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id, content FROM chunks")
    return cursor.fetchall()

def store_embedding(conn, chunk_id, embedding):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO embeddings (chunk_id, embedding) VALUES (?, ?)", 
                   (chunk_id, embedding.tobytes()))
    conn.commit()

def main():
    print("🔍 Loading model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    print("🔗 Connecting to DB...")
    conn = init_db()

    print("📦 Fetching chunks...")
    chunks = fetch_chunks(conn)
    print(f"🧩 Embedding {len(chunks)} chunks")

    for chunk_id, content in tqdm(chunks):
        try:
            embedding = model.encode(content)
            store_embedding(conn, chunk_id, embedding)
        except Exception as e:
            print(f"❌ Failed to embed chunk {chunk_id}: {e}")

    conn.close()
    
    print("✅ Done embedding all chunks!")

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    main()
