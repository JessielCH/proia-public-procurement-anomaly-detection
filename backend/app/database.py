import sqlite3
import os

DB_PATH = "feedback.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS model_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_name TEXT,
            patron_texto TEXT,
            score_ia REAL,
            es_anomalia_real BOOLEAN,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_feedback(doc_name, texto, score, es_anomalia):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO model_feedback (document_name, patron_texto, score_ia, es_anomalia_real)
        VALUES (?, ?, ?, ?)
    ''', (doc_name, texto, score, es_anomalia))
    conn.commit()
    conn.close()