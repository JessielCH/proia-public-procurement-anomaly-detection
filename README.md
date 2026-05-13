# MVP PROIA - Detector de Anomalías en Contratación Pública 🕵️‍♂️📄

![Estado](https://img.shields.io/badge/Estado-En_Desarrollo-blue)
![Licencia](https://img.shields.io/badge/Licencia-MIT-green)
![Python](https://img.shields.io/badge/Python-3.10+-yellow)
![React](https://img.shields.io/badge/React-18_|_Vite-cyan)

Un sistema Full-Stack impulsado por Inteligencia Artificial diseñado para analizar Términos de Referencia (TDRs) y documentos de contratación pública. Utiliza **aprendizaje automático no supervisado** para detectar inconsistencias semánticas, sobre-especificaciones y anomalías basándose estrictamente en la consistencia interna del documento.

## 🚀 Características Principales

- **Análisis de Consistencia Interna:** La IA evalúa el documento contra sí mismo (documento vs. documento). Un patrón se considera anómalo si se desvía del comportamiento semántico general del TDR, sin depender de reglas externas frágiles.
- **Enmascaramiento Semántico (Filtro de Ruido):** El motor identifica y aísla automáticamente cláusulas legales estandarizadas (ej. normativas LOSNCP, firmas de responsabilidad) mediante similitud de coseno, evitando que el "ruido de plantilla" genere falsos positivos.
- **Detección Avanzada de Outliers:** Utiliza _Isolation Forest_ combinado con embeddings multilingües (`paraphrase-multilingual-MiniLM-L12-v2`) para entender el contexto técnico real en español.
- **UX/UI para Usuarios no Técnicos:** Interfaz limpia construida con React y Tailwind CSS. Ofrece retroalimentación visual inmediata, _skeleton loaders_, y explicaciones de anomalías en lenguaje administrativo, no técnico.
- **Despliegue Contenerizado:** Arquitectura lista para producción orquestada completamente con Docker y Docker Compose.

## 🛠️ Arquitectura y Stack Tecnológico

El sistema está dividido en microservicios ligeros para garantizar escalabilidad:

### Backend (Motor IA)

- **Framework:** FastAPI (Python)
- **Procesamiento NLP:** `sentence-transformers`
- **Machine Learning:** `scikit-learn` (Isolation Forest)
- **Extracción de Textos:** `PyMuPDF` (Procesamiento de PDFs complejos)

### Frontend (Dashboard)

- **Core:** React.js + Vite (Node 22)
- **Estilos:** Tailwind CSS (v3.4)
- **Animaciones:** Framer Motion
- **Iconografía:** Lucide React

---

## ⚙️ Instalación y Despliegue Local

### Requisitos Previos

- [Docker](https://www.docker.com/products/docker-desktop) instalado y en ejecución.
- Docker Compose.

### Pasos para levantar el entorno

1. **Clonar el repositorio**

   ```bash
   git clone https://github.com/JessielCH/deteccion_de_anomalias_tdrs.git
   cd deteccion_de_anomalias_tdrs
   ```

2. **Construir las imágenes (Sin usar caché para instalaciones limpias)**

   ```bash
   docker-compose build --no-cache
   ```

3. **Levantar los servicios**

   ```bash
   docker-compose up -d
   ```

4. **Acceder a la aplicación**
   - **Interfaz de Usuario (Frontend):** `http://localhost:5173`
   - **Documentación API (Backend - Swagger):** `http://localhost:8000/docs`

---

## 📊 ¿Cómo funciona la IA? (Flujo de Ejecución)

1. **Ingesta:** El usuario sube un archivo `.pdf`. El motor extrae los bloques de texto descartando ruidos de formato.
2. **Vectorización Multilingüe:** Cada párrafo se convierte en una representación matemática (embedding) usando un modelo profundo optimizado para español.
3. **Escudo Legal (Pre-filtro):** Se calcula la distancia semántica contra una base de conocimiento de "plantillas legales". Los párrafos que superan el 75% de similitud se marcan y se excluyen del análisis de anomalías.
4. **Isolation Forest:** La IA entrena un bosque de aislamiento temporal _exclusivamente_ con el texto técnico del documento para aprender su comportamiento normal (el "centroide").
5. **Puntuación de Anomalía:** Los párrafos que quedan aislados rápidamente por el algoritmo reciben un puntaje de anomalía alto, el cual se normaliza a un porcentaje (0-100%).
6. **Reporte:** El frontend renderiza tarjetas interactivas permitiendo al analista aprobar o rechazar los hallazgos.

---

## 🧹 Comandos Útiles de Mantenimiento

```bash
# Apagar y eliminar volúmenes huérfanos
docker-compose down -v

# Ver logs del motor de IA en tiempo real
docker-compose logs -f backend

# Ver logs de la interfaz web
docker-compose logs -f frontend
```

---

> Desarrollado como solución tecnológica para la auditoría inteligente y prevención de riesgos en la contratación pública.
