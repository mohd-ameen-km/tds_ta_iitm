# preprocess/preprocess.py

import os
import glob
import json
import sqlite3
from uuid import uuid4
import re

DB_PATH = "data/chunks.db"
DISCOURSE_PATH = "data/discourse_posts.json"
COURSE_PATH = "data/tds_course"
CHUNK_SIZE = 500  # characters
CHUNK_OVERLAP = 100

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    chunks = []
    i = 0
    while i < len(text):
        chunk = text[i:i + chunk_size]
        if len(chunk.strip()) > 50:
            chunks.append(chunk.strip())
        i += chunk_size - overlap
    return chunks

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            id TEXT PRIMARY KEY,
            source TEXT,
            type TEXT,
            content TEXT
        )
    """)
    conn.commit()
    return conn

def insert_chunk(conn, source, content, type_):
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chunks (id, source, type, content) VALUES (?, ?, ?, ?)",
        (str(uuid4()), source, type_, content)
    )
    conn.commit()

def process_course_content(conn):
    md_files = glob.glob(os.path.join(COURSE_PATH, "*.md"))
    print(f"📘 Found {len(md_files)} markdown files")
    for md_file in md_files:
        with open(md_file, "r", encoding="utf-8") as f:
            text = f.read()
        cleaned = clean_text(text)
        chunks = chunk_text(cleaned)
        for chunk in chunks:
            insert_chunk(conn, source=md_file, content=chunk, type_="markdown")
    print("✅ Finished processing course content")

def process_discourse(conn):
    with open(DISCOURSE_PATH, "r", encoding="utf-8") as f:
        threads = json.load(f)
    print(f"💬 Found {len(threads)} discourse threads")
    for thread in threads:
        for post in thread["posts"]:
            # Safely extract content
            if isinstance(post, dict) and "content" in post:
                cleaned = clean_text(post["content"])
                chunks = chunk_text(cleaned)
                for chunk in chunks:
                    insert_chunk(conn, source=thread["url"], content=chunk, type_="discourse")
            elif isinstance(post, str):  # fallback for old format
                cleaned = clean_text(post)
                chunks = chunk_text(cleaned)
                for chunk in chunks:
                    insert_chunk(conn, source=thread["url"], content=chunk, type_="discourse")
            else:
                print("⚠️ Skipping malformed post:", post)
    print("✅ Finished processing discourse posts")


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    conn = init_db()
    process_course_content(conn)
    process_discourse(conn)
    conn.close()
    print("🎉 All data preprocessed and stored in SQLite!")
