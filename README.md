# PROIA - Auditoría Semántica y Topológica de TDRs 🛢️🔍

**PROIA** (Procesamiento y Reconocimiento de Operaciones Irregulares Algorítmicas) es un ecosistema de **Inteligencia Artificial No Supervisada** diseñado para detectar direccionamiento y colusión en Términos de Referencia (TDRs) y pliegos de contratación pública, específicamente adaptado para EP Petroecuador.

## Arquitectura (V7.0)

El sistema opera bajo un pipeline híbrido:

1. **Sentence-BERT:** Vectorización semántica profunda de textos legales/técnicos.
2. **t-SNE & DBSCAN:** Análisis Topológico de Datos (TDA) para mapeo de complejos simpliciales y detección de anomalías por densidad espacial.
3. **Isolation Forest:** Aislamiento transaccional estocástico.
4. **TF-IDF:** Extracción estadística de Red Flags sin uso de diccionarios predefinidos (cero sesgos).

## Tecnologías

- Python 3.10+
- Streamlit (Frontend Forense)
- Scikit-Learn & PyTorch
- Plotly & PyVis

## Ejecución Local

````bash
# 1. Ejecutar el pipeline de ingesta (Lee PDFs y genera matriz matemática)
python ingestor_pdfs_v7.py

# 2. Levantar el Laboratorio Forense (Dashboard)
streamlit run dashboard_tdr_v7.py# PROIA - Auditoría Semántica y Topológica de TDRs 🛢️🔍

**PROIA** (Procesamiento y Reconocimiento de Operaciones Irregulares Algorítmicas) es un ecosistema de **Inteligencia Artificial No Supervisada** diseñado para detectar direccionamiento y colusión en Términos de Referencia (TDRs) y pliegos de contratación pública, específicamente adaptado para EP Petroecuador.

## Arquitectura (V7.0)
El sistema opera bajo un pipeline híbrido:
1. **Sentence-BERT:** Vectorización semántica profunda de textos legales/técnicos.
2. **t-SNE & DBSCAN:** Análisis Topológico de Datos (TDA) para mapeo de complejos simpliciales y detección de anomalías por densidad espacial.
3. **Isolation Forest:** Aislamiento transaccional estocástico.
4. **TF-IDF:** Extracción estadística de Red Flags sin uso de diccionarios predefinidos (cero sesgos).

## Tecnologías
* Python 3.10+
* Streamlit (Frontend Forense)
* Scikit-Learn & PyTorch
* Plotly & PyVis

## Ejecución Local
```bash
# 1. Ejecutar el pipeline de ingesta (Lee PDFs y genera matriz matemática)
python ingestor_pdfs_v7.py

# 2. Levantar el Laboratorio Forense (Dashboard)
streamlit run dashboard_tdr_v7.py
````
