import chromadb
from chromadb.config import Settings

# Configuración de base de datos vectorial persistente
client = chromadb.PersistentClient(path="./chroma_db")

def get_collection(name="tdr_analysis"):
    return client.get_or_create_collection(name=name)