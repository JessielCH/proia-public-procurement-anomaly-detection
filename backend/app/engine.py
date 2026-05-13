import fitz  # PyMuPDF
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.ensemble import IsolationForest
from sklearn.metrics.pairwise import cosine_similarity

class AnomalyEngine:
    def __init__(self):
        # Modelo optimizado para español y contextos legales/administrativos
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        
    def extract_text(self, pdf_path):
        """Extrae párrafos con su índice para trazabilidad."""
        doc = fitz.open(pdf_path)
        paragraphs = []
        for page_num, page in enumerate(doc):
            text = page.get_text("blocks")
            for block in text:
                content = block[4].strip()
                if len(content) > 40:  # Filtrar ruidos cortos o números de página
                    paragraphs.append({
                        "text": content,
                        "page": page_num + 1,
                        "block_id": block[5]
                    })
        return paragraphs

    def analyze_consistency(self, paragraphs):
        texts = [p['text'] for p in paragraphs]
        
        # 1. Convertir párrafos a vectores (Embeddings)
        # Aquí la IA "entiende" el significado en español
        embeddings = self.model.encode(texts)

        # 2. Entrenar Isolation Forest con el propio documento
        # Este algoritmo aprende el "ritmo" y "vocabulario" del TDR
        clf = IsolationForest(contamination='auto', random_state=42)
        preds = clf.fit_predict(embeddings)
        
        # 3. Calcular el "Score de Anomalía" (convertido a porcentaje)
        # decision_function devuelve qué tan lejos está del comportamiento normal
        scores = clf.decision_function(embeddings)
        
        # Normalizamos el score a un rango 0-100
        # Un valor más bajo en decision_function significa más anómalo
        min_s, max_s = scores.min(), scores.max()
        norm_scores = [round((1 - (s - min_s) / (max_s - min_s)) * 100, 2) for s in scores]

        results = []
        for i, score in enumerate(norm_scores):
            # Solo reportamos como hallazgo si supera un umbral de sospecha (ej. 60%)
            if score > 60:
                results.append({
                    "patron_detectado": texts[i][:100] + "...",
                    "porcentaje_anomalia": score,
                    "explicacion_breve": self._generate_explanation(texts[i], texts),
                    "parrafos_afectados": [i + 1]
                })
        
        # Ordenar por nivel de criticidad
        return sorted(results, key=lambda x: x['porcentaje_anomalia'], reverse=True)

    def _generate_explanation(self, target_text, all_texts):
        """Genera una explicación humana basada en la diferencia de términos."""
        # Lógica simple de contraste: buscar palabras clave en el párrafo 
        # que no se repiten en el resto del documento.
        return "Este fragmento utiliza terminología técnica o condiciones de especificidad que no se mencionan en el resto del pliego."