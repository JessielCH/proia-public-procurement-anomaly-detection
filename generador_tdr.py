import pandas as pd
import numpy as np
import random
import networkx as nx
from sentence_transformers import SentenceTransformer
from sklearn.cluster import DBSCAN
from sklearn.manifold import TSNE
from sklearn.metrics.pairwise import cosine_similarity
import os

# --- CONFIGURACIÓN ---
OUTPUT_DIR = "./data/output"
os.makedirs(OUTPUT_DIR, exist_ok=True)
RUTA_CSV = os.path.join(OUTPUT_DIR, "analisis_tdr_proia.csv")

print("🚀 Iniciando Motor PROIA: Análisis No Supervisado de TDRs...")

# 1. Generación de TDRs Sintéticos
NUM_TDRS = 300
tdrs = []
proveedores_normales = [f"Empresa Lícita {i} S.A." for i in range(50)]
cartel = ["Corporación X-200", "Suministros Exclusivos LLC", "Frente Colusorio S.A."]

textos_normales = [
    "Servicio de mantenimiento preventivo de equipos. Se requiere personal técnico calificado y repuestos estándar compatibles con normas ISO generales. Promueve libre competencia.",
    "Adquisición de insumos de oficina y computación. Especificaciones abiertas, procesadores de generación reciente, memoria RAM estándar.",
    "Contratación de servicios de limpieza para instalaciones. Se requiere uso de productos biodegradables genéricos."
]

textos_dirigidos = [
    "El proveedor debe suministrar válvulas con certificación exclusiva X-200, patente cerrada. Se requiere carta de exclusividad del fabricante originario en Europa.",
    "Licencias de software de base de datos privativa marca Y-Enterprise, versión 14.5.2 estricta, no se aceptan equivalencias de código abierto bajo ninguna circunstancia.",
    "Mantenimiento de turbinas. El oferente debe tener 25 años exactos de experiencia en el modelo Z-Beta, exigiendo herramientas con código de serie restrictivo."
]

print("📝 Generando TDRs y simulando participaciones...")
for i in range(NUM_TDRS):
    es_anomalo = random.random() < 0.10 # 10% de TDRs dirigidos
    
    if es_anomalo:
        texto = random.choice(textos_dirigidos)
        postulantes = random.sample(cartel, k=random.randint(2, 3)) # El cartel siempre participa aquí
    else:
        texto = random.choice(textos_normales)
        postulantes = random.sample(proveedores_normales, k=random.randint(3, 8))
        
    tdrs.append({
        "id_tdr": f"TDR-2026-{str(i).zfill(4)}",
        "texto_especificaciones": texto,
        "proveedores_participantes": ", ".join(postulantes),
        "es_anomalo_real": 1 if es_anomalo else 0
    })

df = pd.DataFrame(tdrs)

# 2. Análisis Semántico Profundo (AFFAIR + Sentence-BERT)
print("🧠 Cargando modelo LLM (Sentence-BERT)... Generando Embeddings densos...")
modelo_llm = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
embeddings = modelo_llm.encode(df['texto_especificaciones'].tolist())

# Cálculo de la "Prueba del Copy-Paste" (Similitud Coseno máxima con otro TDR)
print("🔍 Calculando similitud semántica cruzada...")
sim_matrix = cosine_similarity(embeddings)
np.fill_diagonal(sim_matrix, 0) # Ignorar la similitud del documento consigo mismo
df['similitud_maxima'] = sim_matrix.max(axis=1) * 100

# Reducimos a 2D usando t-SNE (Ideal para ver formas topológicas)
print("🌌 Aplicando t-SNE para revelar la forma del mercado en 2D...")
tsne = TSNE(n_components=2, perplexity=15, random_state=42)
componentes_2d = tsne.fit_transform(embeddings)
df['dim_x'] = componentes_2d[:, 0]
df['dim_y'] = componentes_2d[:, 1]

# 3. Detección Topológica No Supervisada (DBSCAN en 2D)
print("🗺️ Buscando 'Islas' topológicas con DBSCAN...")
# Usamos un eps ajustado para el espacio 2D de t-SNE
clustering = DBSCAN(eps=4.0, min_samples=3).fit(componentes_2d)
df['alerta_direccionamiento'] = np.where(clustering.labels_ == -1, 1, 0)

# 4. Cálculo Estructural (Redes Bipartitas para Colusión)
print("🕸️ Calculando centralidad en la red de postulaciones...")
B = nx.Graph()
for _, row in df.iterrows():
    tdr = row['id_tdr']
    B.add_node(tdr, bipartite=0)
    proveedores = row['proveedores_participantes'].split(", ")
    for prov in proveedores:
        B.add_node(prov, bipartite=1)
        B.add_edge(tdr, prov)

grados = nx.degree_centrality(B)
df['riesgo_colusion_max'] = df['proveedores_participantes'].apply(
    lambda x: max([grados.get(p, 0) for p in x.split(", ")])
)

df.to_csv(RUTA_CSV, index=False)
print("✅ Procesamiento completado. Base de datos lista para el Dashboard.")