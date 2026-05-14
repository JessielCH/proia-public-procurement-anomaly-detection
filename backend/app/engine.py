import fitz  # PyMuPDF
import numpy as np
import networkx as nx
import re
import umap
import io
import base64
import matplotlib
matplotlib.use('Agg') # Modo headless para funcionar dentro de Docker sin interfaz gráfica
import matplotlib.pyplot as plt

from nltk.corpus import stopwords
from sentence_transformers import SentenceTransformer
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.metrics.pairwise import cosine_similarity

class AnomalyEngine:
    def __init__(self):
        # El modelo se carga directamente desde la carpeta interna de Docker (model_cache)
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        
        # Palabras protegidas para no perder el contexto condicional
        palabras_protegidas = {"sin", "con", "no", "si", "debe", "deberá", "excluyente"}
        self.stop_words = set(stopwords.words('spanish')) - palabras_protegidas
        
        # Extirpador de contexto normativo (Boilerplate legal)
        self.patrones_legales = [
            r"ley orgánica del sistema nacional de contratación pública",
            r"reglamento general", r"losncp", r"sercop", r"incpe",
            r"normas técnicas de control interno", r"contraloría general del estado",
            r"resolución nro", r"artículo \d+", r"literal \w"
        ]

        # Patrones restrictivos (Marcas y direccionamiento duro)
        self.patrones_restrictivos = [
            r"\bexclusivamente\b", r"\búnicamente\b", r"\bobligatoriamente\b",
            r"\bno se aceptará\b", r"\bmarca\b", r"\bfabricante\b", r"\bpartner\b",
            r"\bdistribuidor autorizado\b", r"\brepresentante autorizado\b"
        ]

    def extract_text(self, pdf_path):
        """Extrae párrafos del PDF filtrando ruido demasiado corto."""
        doc = fitz.open(pdf_path)
        paragraphs = []
        for page_num, page in enumerate(doc):
            text = page.get_text("blocks")
            for block in text:
                content = block[4].strip()
                if len(content) > 50: 
                    paragraphs.append({"text": content, "page": page_num + 1})
        return paragraphs

    def _clean_text(self, text):
        """Limpia el texto de jerga legal, puntuación y stopwords para la IA."""
        text_lower = text.lower()
        
        # 1. Limpiar jerga legal/normativa
        for patron in self.patrones_legales:
            text_lower = re.sub(patron, "", text_lower)
            
        # 2. Limpieza de puntuación y stopwords
        text_clean = re.sub(r'[^\w\s]', '', text_lower)
        words = [w for w in text_clean.split() if w not in self.stop_words]
        
        # Preservar el texto si la limpieza lo dejó casi vacío
        if len(words) < 5: 
            return text 
        return " ".join(words)

    def analyze_consistency(self, paragraphs):
        original_texts = [p['text'] for p in paragraphs]
        cleaned_texts = [self._clean_text(t) for t in original_texts]
        
        # Requisito mínimo para estadística poblacional
        if len(cleaned_texts) < 10: 
            return {"findings": [], "graficos": None}

        # Vectorización Semántica
        embeddings = self.model.encode(cleaned_texts)

        # ==========================================
        # MOTOR 1: UMAP (Reducción Dimensional 2D)
        # ==========================================
        reducer = umap.UMAP(n_neighbors=min(5, len(embeddings)-1), min_dist=0.1, n_components=2, random_state=42,init='random')
        umap_embeddings = reducer.fit_transform(embeddings)

        # ==========================================
        # MOTOR 2: Local Outlier Factor (Densidad UMAP)
        # ==========================================
        lof = LocalOutlierFactor(n_neighbors=min(5, len(umap_embeddings)-1), contamination='auto')
        lof.fit_predict(umap_embeddings)
        scores_lof = -lof.negative_outlier_factor_ 
        min_lof, max_lof = scores_lof.min(), scores_lof.max()
        norm_lof = [(s - min_lof) / (max_lof - min_lof + 1e-10) for s in scores_lof]

        # ==========================================
        # MOTOR 3: Isolation Forest (Estadística Clásica)
        # ==========================================
        clf = IsolationForest(contamination='auto', random_state=42)
        scores_if = 1 - ((clf.fit(embeddings).decision_function(embeddings) - -0.5) / 1.0)
        
        # ==========================================
        # MOTOR 4: TDA Grafos (Topología de Red)
        # ==========================================
        similarity = cosine_similarity(embeddings)
        G = nx.Graph()
        for i in range(len(paragraphs)):
            G.add_node(i)
            for j in range(i+1, len(paragraphs)):
                # Umbral de similitud para crear una arista
                if similarity[i][j] > 0.40:
                    G.add_edge(i, j, weight=similarity[i][j])
        
        centrality = nx.degree_centrality(G)

        # ==========================================
        # EVALUACIÓN DE RESULTADOS
        # ==========================================
        results = []
        for i, p in enumerate(paragraphs):
            texto_original = original_texts[i]
            texto_minusculas = texto_original.lower()
            word_count = len(texto_original.split())

            graph_iso = 1.0 - centrality.get(i, 0)
            
            # SCORE HÍBRIDO: 40% Isolation Forest + 30% Grafo + 30% UMAP LOF
            final_score = (scores_if[i] * 40) + (graph_iso * 30) + (norm_lof[i] * 100 * 30)
            
            # Reglas duras: Bonus de riesgo por restrictividad de marcas
            tiene_restrictividad = any(re.search(pat, texto_minusculas) for pat in self.patrones_restrictivos)
            if tiene_restrictividad:
                final_score += 15

            if final_score > 68:
                tipo = "Inconsistencia Semántica"
                razones = []
                
                if final_score > 80 and word_count > 60 and graph_iso > 0.85:
                    tipo = "⚠️ POSIBLE DIRECCIONAMIENTO"
                    razones.append("Aislamiento estructural (TDA Grafo) y alta especificidad técnica.")
                
                if norm_lof[i] > 0.8:
                    razones.append("Distante del clúster principal (Anomalía de Densidad UMAP).")
                    
                if tiene_restrictividad:
                    tipo = "⛔ RESTRICCIÓN DE MARCAS"
                    razones.append("Contiene palabras que exigen exclusividad o marcas específicas.")

                if not razones:
                    razones.append("El lenguaje estadísticamente no se alinea con la consistencia general del TDR.")

                results.append({
                    "patron_detectado": texto_original[:200] + "...",
                    "porcentaje_anomalia": min(round(final_score, 2), 99.9),
                    "explicacion_breve": f"{tipo}: {' '.join(razones)}",
                    "parrafos_afectados": [p.get('page', i+1)]
                })
                
        # ==========================================
        # GENERACIÓN DE GRÁFICOS (Base64)
        # ==========================================
        
        # 1. Gráfico UMAP
        plt.figure(figsize=(6, 4))
        plt.scatter(umap_embeddings[:, 0], umap_embeddings[:, 1], c=norm_lof, cmap='coolwarm', s=50, alpha=0.7)
        plt.title("Mapa Semántico (UMAP + Densidad LOF)", fontsize=10)
        plt.axis('off')
        buf_umap = io.BytesIO()
        plt.savefig(buf_umap, format='png', bbox_inches='tight', transparent=True)
        plt.close()
        img_umap = f"data:image/png;base64,{base64.b64encode(buf_umap.getvalue()).decode('utf-8')}"

        # 2. Gráfico TDA Grafo
        plt.figure(figsize=(6, 4))
        pos = nx.spring_layout(G, seed=42)
        # Nodos con baja centralidad (aislados) se pintan más intensos en el colormap Reds
        node_colors = [1.0 - centrality.get(n, 0) for n in G.nodes()]
        nx.draw(G, pos, node_size=60, node_color=node_colors, cmap=plt.cm.Reds, edge_color='#e2e8f0', alpha=0.8)
        plt.title("Estructura Topológica (Nodos rojos = Aislados)", fontsize=10)
        buf_grafo = io.BytesIO()
        plt.savefig(buf_grafo, format='png', bbox_inches='tight', transparent=True)
        plt.close()
        img_grafo = f"data:image/png;base64,{base64.b64encode(buf_grafo.getvalue()).decode('utf-8')}"

        return {
            "findings": sorted(results, key=lambda x: x['porcentaje_anomalia'], reverse=True),
            "graficos": {
                "umap": img_umap,
                "grafo": img_grafo
            }
        }