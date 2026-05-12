import fitz
import pandas as pd
import numpy as np
import os
import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.manifold import TSNE
from sklearn.cluster import DBSCAN
from sklearn.ensemble import IsolationForest
from sklearn.feature_extraction.text import TfidfVectorizer

CARPETA_PDFS = "./data/input"
OUTPUT_CSV = "./data/output/tdrs_reales_vectorizados.csv"

def extractor_quirurgico(texto):
    texto = re.sub(r'\s+', ' ', texto)
    texto = re.sub(r'Este documento es de propiedad exclusiva de EP PETROECUADOR.*?(autorizado|Formato).*?\d{4}', '', texto, flags=re.IGNORECASE)
    texto = re.sub(r'CLASIFICACIÓN: PÚBLICO', '', texto, flags=re.IGNORECASE)
    texto = re.sub(r'PETROECUADOR ESPECIFICACIONES T[EÉ]CNICAS Y T[EÉ]RMINOS DE REFERENCIA.*?Versi[oó]n: \d{2}', '', texto, flags=re.IGNORECASE)
    
    patron_core = r'(?:OBJETO DE LA CONTRATACI[OÓ]N|ESPECIFICACIONES T[EÉ]CNICAS)(.*?)(?:FIRMAS|ANEXOS|OBLIGACIONES DEL CONTRATISTA|$)'
    match = re.search(patron_core, texto, re.IGNORECASE)
    texto_analisis = match.group(1).strip() if match else texto
    texto_analisis = re.sub(r'La Constituci[oó]n de la Rep[uú]blica del Ecuador.*?(?=El propósito|En la operación|Para el presente)', '', texto_analisis, flags=re.IGNORECASE)
    
    return texto_analisis[:5000]

def procesar_directorio():
    datos = []
    for archivo in os.listdir(CARPETA_PDFS):
        if archivo.endswith(".pdf"):
            try:
                doc = fitz.open(os.path.join(CARPETA_PDFS, archivo))
                texto_completo = "".join([pagina.get_text() for pagina in doc])
                texto_limpio = extractor_quirurgico(texto_completo)
                if len(texto_limpio.strip()) > 50:
                    datos.append({"id_tdr": archivo, "texto_especificaciones": texto_limpio})
            except Exception as e:
                pass
    return pd.DataFrame(datos)

if __name__ == "__main__":
    df = procesar_directorio()
    if not df.empty:
        print("🧠 Vectorizando Petro vs Petro...")
        modelo = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        embeddings = modelo.encode(df['texto_especificaciones'].tolist())

        # SIMILITUD PETRO VS PETRO
        sim_matrix = cosine_similarity(embeddings)
        np.fill_diagonal(sim_matrix, 0)
        
        # TOPOLOGÍA Y ANOMALÍAS
        tsne = TSNE(n_components=2, perplexity=min(10, max(1, len(df)-1)), random_state=42)
        coords = tsne.fit_transform(embeddings)
        df['dim_x'], df['dim_y'] = coords[:, 0], coords[:, 1]
        
        iso_forest = IsolationForest(contamination=0.08, random_state=42)
        df['score_isolation'] = iso_forest.fit_predict(embeddings)
        clustering = DBSCAN(eps=3.5, min_samples=2).fit(coords)
        df['alerta_direccionamiento'] = np.where((clustering.labels_ == -1) | (df['score_isolation'] == -1), 1, 0)

        # BÚSQUEDA DEL GEMELO HISTÓRICO Y RED FLAGS
        vectorizer = TfidfVectorizer(max_df=0.85, min_df=2, stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(df['texto_especificaciones'])
        feature_names = vectorizer.get_feature_names_out()

        gemelos = []
        red_flags = []
        similitudes = []

        for i in range(len(df)):
            if df['alerta_direccionamiento'].iloc[i] == 1:
                # 1. Encontrar el TDR Normal más parecido (El Gemelo)
                similitudes_i = sim_matrix[i].copy()
                # Solo buscamos entre los normales
                similitudes_i[df['alerta_direccionamiento'] == 1] = -1 
                idx_gemelo = np.argmax(similitudes_i)
                
                gemelos.append(df['id_tdr'].iloc[idx_gemelo])
                similitudes.append(similitudes_i[idx_gemelo] * 100)
                
                # 2. Extraer Red Flags (Palabras únicas de la anomalía que no están en el corpus normal)
                fila = tfidf_matrix.getrow(i).toarray()[0]
                top_indices = fila.argsort()[-8:][::-1] # Extraemos las 8 palabras más atípicas
                palabras_top = [feature_names[idx] for idx in top_indices if fila[idx] > 0]
                red_flags.append(", ".join(palabras_top).upper())
            else:
                gemelos.append("N/A")
                similitudes.append(0.0)
                red_flags.append("N/A")

        df['id_gemelo_historico'] = gemelos
        df['porcentaje_similitud_gemelo'] = similitudes
        df['red_flags_detectadas'] = red_flags

        os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
        df.to_csv(OUTPUT_CSV, index=False)
        print(f"✅ ¡Pipeline V7.0 (Petro vs Petro) completado! Guardados {len(df)} TDRs.")