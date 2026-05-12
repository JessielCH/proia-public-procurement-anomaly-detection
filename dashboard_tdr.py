import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import os
from sklearn.neighbors import NearestNeighbors

st.set_page_config(page_title="PROIA: Auditoría Petro vs Petro", layout="wide", page_icon="🛢️")

DATA_PATH = "./data/output/tdrs_reales_vectorizados.csv"

@st.cache_data
def load_data():
    if not os.path.exists(DATA_PATH): return pd.DataFrame()
    return pd.read_csv(DATA_PATH)

df = load_data()

if df.empty:
    st.error("⚠️ Ejecuta el script de ingesta (ingestor_pdfs_v7.py) primero.")
    st.stop()

st.title("🛢️ Laboratorio Forense PROIA: Análisis Petro vs Petro")
st.markdown("Fiscalización pre-contractual. Detección de alteraciones y Red Flags en Pliegos y TDRs.")

with st.container():
    k1, k2, k3 = st.columns(3)
    k1.metric("TDRs Procesados", len(df))
    k2.metric("TDRs con Alertas Topológicas", df['alerta_direccionamiento'].sum(), delta="Desviación del Estándar", delta_color="inverse")
    k3.metric("Motor Analítico", "Comparativa Histórica + TF-IDF Deltas")

st.divider()

tabs = st.tabs(["🌌 Topología del Mercado", "📄 Comparador de Gemelos (Rayos X)", "🚩 Matriz de Red Flags"])

# --- TAB 1: GEOMETRÍA TOPOLÓGICA (TDA) ---
with tabs[0]:
    st.header("Análisis de Complejos Simpliciales (TDA)")
    st.info("🔵 **TDRs Estándar** (Patrón normal de Petroecuador) | 🔴 **TDRs Anómalos** (Desviación estructural).")
    
    coords = df[['dim_x', 'dim_y']].values
    nn = NearestNeighbors(n_neighbors=5).fit(coords)
    distances, indices = nn.kneighbors(coords)
    
    fig_tda = go.Figure()
    edge_x, edge_y = [], []
    for i in range(len(coords)):
        for j in indices[i][1:]:
            edge_x.extend([coords[i, 0], coords[j, 0], None])
            edge_y.extend([coords[i, 1], coords[j, 1], None])

    fig_tda.add_trace(go.Scatter(x=edge_x, y=edge_y, mode='lines', line=dict(color='rgba(200, 200, 200, 0.4)', width=1), hoverinfo='none', showlegend=False))

    for estado, color, label in [(0, '#3498db', 'TDR Estándar (Petroecuador)'), (1, '#e74c3c', 'TDR Desviado (Alerta)')]:
        subset = df[df['alerta_direccionamiento'] == estado]
        fig_tda.add_trace(go.Scatter(
            x=subset['dim_x'], y=subset['dim_y'], mode='markers', name=label,
            marker=dict(size=14 if estado == 0 else 20, color=color, line=dict(width=2, color='white')),
            text=subset['id_tdr'], hovertemplate="<b>%{text}</b><extra></extra>"
        ))

    fig_tda.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', height=600, xaxis=dict(visible=False), yaxis=dict(visible=False))
    st.plotly_chart(fig_tda, use_container_width=True)

# --- TAB 2: COMPARADOR DE GEMELOS (RAYOS X) ---
with tabs[1]:
    st.header("Análisis de Desviación Documental")
    st.markdown("Compara el TDR Anómalo directamente con el TDR histórico más similar de EP Petroecuador.")
    
    alertas = df[df['alerta_direccionamiento'] == 1]
    
    if not alertas.empty:
        seleccion = st.selectbox("Seleccione un Documento con Alerta:", alertas['id_tdr'])
        tdr_actual = alertas[alertas['id_tdr'] == seleccion].iloc[0]
        
        id_gemelo = tdr_actual['id_gemelo_historico']
        tdr_gemelo = df[df['id_tdr'] == id_gemelo].iloc[0] if id_gemelo != "N/A" else None
        
        st.metric("Índice de Similitud (Copy-Paste) con Histórico", f"{tdr_actual['porcentaje_similitud_gemelo']:.1f}%")
        
        st.warning(f"🚩 **RED FLAGS (Términos Estadísticamente Anómalos):** {tdr_actual['red_flags_detectadas']}")
        
        c1, c2 = st.columns(2)
        with c1:
            st.error(f"🔴 **TDR EN REVISIÓN**: `{tdr_actual['id_tdr']}`")
            texto_anomalo = str(tdr_actual['texto_especificaciones'])
            
            # Resaltar las Red Flags en el texto
            for flag in str(tdr_actual['red_flags_detectadas']).split(", "):
                if flag and flag != "N/A":
                    import re
                    texto_anomalo = re.sub(f"(?i)({flag.strip()})", r"**_\1_** 🔴", texto_anomalo)
                    
            with st.container(height=500):
                st.markdown(texto_anomalo)
                
        with c2:
            st.success(f"🟢 **GEMELO HISTÓRICO (Base Normal)**: `{id_gemelo}`")
            if tdr_gemelo is not None:
                with st.container(height=500):
                    st.markdown(str(tdr_gemelo['texto_especificaciones']))
            else:
                st.info("No se encontró un gemelo claro. Este documento es completamente inédito.")
    else:
        st.success("No hay TDRs con alertas estructurales.")

# --- TAB 3: MATRIZ DE RED FLAGS ---
with tabs[2]:
    st.header("Consolidado de Red Flags Institucionales")
    st.markdown("Tabla forense de los documentos que rompen el patrón histórico de Petroecuador.")
    
    alertas_df = df[df['alerta_direccionamiento'] == 1][['id_tdr', 'id_gemelo_historico', 'porcentaje_similitud_gemelo', 'red_flags_detectadas']]
    
    if not alertas_df.empty:
        alertas_df.columns = ["Documento Sospechoso", "Pliego Base (Copiado de)", "Similitud (%)", "Red Flags Extraídas"]
        st.dataframe(alertas_df, use_container_width=True, hide_index=True)
    else:
        st.success("Ecosistema documental limpio.")