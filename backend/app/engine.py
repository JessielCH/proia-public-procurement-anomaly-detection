import fitz
import numpy as np
import networkx as nx
import re
import umap
import io
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from nltk.corpus import stopwords
from sentence_transformers import SentenceTransformer
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler

class AnomalyEngine:
    def __init__(self):
        # Modelo 100% local en caché de Docker
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        
        palabras_protegidas = {"sin", "con", "no", "si", "debe", "deberá", "excluyente"}
        self.stop_words = set(stopwords.words('spanish')) - palabras_protegidas
        
        self.patrones_legales = [
            r"ley orgánica", r"reglamento general", r"losncp", r"sercop", 
            r"artículo \d+", r"literal \w", r"contraloría general"
        ]
        
        # Diccionario de palabras restrictivas para identificar Red Flags explícitas
        self.patrones_restrictivos = [
            r"\bexclusivamente\b", r"\búnicamente\b", r"\bobligatoriamente\b", 
            r"\bmarca\b", r"\bfabricante\b", r"\bdistribuidor autorizado\b", r"\bpartner\b",
            r"\bsolamente\b", r"\bindispensable\b", r"\bno se aceptará\b"
        ]

        # Filtro de Patrones Humanos Naturales (Creadores del TDR y Firmas)
        self.patrones_humanos = [
            "ELABORADO POR", "REVISADO POR", "AUTORIZADO POR", 
            "APROBADO POR", "CARGO:", "NOMBRE:", "FIRMA ELECTRÓNICA",
            "CÉDULA:", "DOCUMENTO FIRMADO ELECTRÓNICAMENTE", "ING."
        ]

    def extract_text(self, pdf_path):
        doc = fitz.open(pdf_path)
        paragraphs = []
        
        for page_num, page in enumerate(doc):
            text = page.get_text("blocks")
            for block in text:
                content = block[4].strip()
                
                # Filtro humano para firmas
                if any(patron in content.upper() for patron in self.patrones_humanos):
                    continue
                
                if len(content) > 60: 
                    paragraphs.append({"text": content, "page": page_num + 1})
                    
        return paragraphs

    def _clean_text(self, text):
        text_lower = text.lower()
        for patron in self.patrones_legales:
            text_lower = re.sub(patron, "", text_lower)
            
        text_clean = re.sub(r'[^\w\s]', '', text_lower)
        words = [w for w in text_clean.split() if w not in self.stop_words]
        
        if len(words) < 5: return text
        return " ".join(words)

    def analyze_consistency(self, paragraphs):
        original_texts = [p['text'] for p in paragraphs]
        cleaned_texts = [self._clean_text(t) for t in original_texts]
        
        if len(cleaned_texts) < 10: return {"findings": [], "graficos": None}
        embeddings = self.model.encode(cleaned_texts)

        # MOTOR 1: UMAP + LOF
        reducer = umap.UMAP(n_neighbors=min(5, len(embeddings)-1), n_components=2, random_state=42, init='random')
        umap_emb = reducer.fit_transform(embeddings)
        lof = LocalOutlierFactor(n_neighbors=min(5, len(umap_emb)-1))
        lof.fit_predict(umap_emb)
        scores_lof = -lof.negative_outlier_factor_

        # MOTOR 2: Isolation Forest
        iforest = IsolationForest(random_state=42).fit(embeddings)
        scores_if = -iforest.decision_function(embeddings)

        # MOTOR 3: TDA Grafos
        similarity = cosine_similarity(embeddings)
        G = nx.Graph()
        for i in range(len(paragraphs)):
            G.add_node(i)
        for i in range(len(paragraphs)):
            for j in range(i+1, len(paragraphs)):
                if similarity[i][j] > 0.45: G.add_edge(i, j)
                    
        centrality = nx.degree_centrality(G)
        scores_graph = np.array([1.0 - centrality.get(i, 0) for i in range(len(paragraphs))])

        # Normalización MinMaxScaler
        scaler = MinMaxScaler(feature_range=(0, 1))
        norm_if = scaler.fit_transform(scores_if.reshape(-1, 1)).flatten()
        norm_lof = scaler.fit_transform(scores_lof.reshape(-1, 1)).flatten()
        norm_graph = scaler.fit_transform(scores_graph.reshape(-1, 1)).flatten()

        results = []
        for i, p in enumerate(paragraphs):
            texto_original = original_texts[i]
            texto_minusculas = texto_original.lower()
            word_count = len(texto_original.split())

            graph_iso = norm_graph[i]
            final_score = (norm_if[i] * 40) + (graph_iso * 30) + (norm_lof[i] * 30)
            
            # Buscar qué palabras restrictivas exactas se encendieron
            alertas_encontradas = []
            for pat in self.patrones_restrictivos:
                coincidencias = re.findall(pat, texto_minusculas)
                if coincidencias:
                    alertas_encontradas.extend(coincidencias)
            
            # Eliminar duplicados de palabras encontradas
            alertas_encontradas = list(set(alertas_encontradas))

            if alertas_encontradas:
                final_score = min(final_score + 20, 100)

            # Si el nivel de riesgo supera el umbral, creamos la alerta gerencial
            if final_score > 60:
                red_flags = []
                
                # Caso 1: Se encontraron palabras excluyentes directas
                if alertas_encontradas:
                    palabras_clave = ", ".join([f"'{w}'" for w in alertas_encontradas])
                    red_flags.append(f"⛔ TÉRMINOS EXCLUYENTES: Se detectó el uso de {palabras_clave}. Al exigir marcas o condiciones cerradas se rompe el principio de libre competencia.")
                
                # Caso 2: El párrafo está totalmente aislado (Cláusula sembrada)
                if graph_iso > 0.85:
                    red_flags.append("⚠️ CLÁUSULA AISLADA: Este párrafo contiene requisitos técnicos exageradamente específicos que no guardan coherencia con el resto del documento. Podría tratarse de un requisito 'sembrado' a medida.")
                
                # Caso 3: Desviación estadística (Redacción inusual)
                if norm_if[i] > 0.80 or norm_lof[i] > 0.80:
                    red_flags.append("🚨 DESVIACIÓN INUSUAL: La complejidad o estructuración de este texto difiere completamente del estándar del TDR, indicando una condición atípica que requiere revisión.")

                # Si el algoritmo general saltó pero no encajó en las anteriores de forma severa
                if not red_flags:
                    red_flags.append("🔍 ALERTAS DE REDACCIÓN: Requisitos técnicos con una densidad inusual de especificaciones comparado con el promedio del pliego.")

                # Combinamos los hallazgos en un solo texto fluido para el jefe/gerente
                explicacion_gerencial = " ".join(red_flags)

                results.append({
                    "patron_detectado": texto_original[:250] + "...",
                    "porcentaje_anomalia": round(final_score, 2),
                    "explicacion_breve": explicacion_gerencial,
                    "parrafos_afectados": [p['page']]
                })

        # Generación de gráficos (Mapeo seguro)
        plt.figure(figsize=(6,4))
        plt.scatter(umap_emb[:,0], umap_emb[:,1], c=norm_lof, cmap='coolwarm')
        plt.axis('off')
        buf_u = io.BytesIO()
        plt.savefig(buf_u, format='png')
        plt.close()
        img_u = f"data:image/png;base64,{base64.b64encode(buf_u.getvalue()).decode()}"

        plt.figure(figsize=(6,4))
        pos = nx.spring_layout(G, seed=42)
        colors_mapped = [norm_graph[node] for node in G.nodes()]
        nx.draw(G, pos, node_size=50, node_color=colors_mapped, cmap=plt.cm.Reds, edge_color='#e2e8f0', alpha=0.8)
        plt.axis('off')
        buf_g = io.BytesIO()
        plt.savefig(buf_g, format='png')
        plt.close()
        img_g = f"data:image/png;base64,{base64.b64encode(buf_g.getvalue()).decode()}"

        return {
            "findings": sorted(results, key=lambda x: x['porcentaje_anomalia'], reverse=True),
            "graficos": {"umap": img_u, "grafo": img_g}
        }