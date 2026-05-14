import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Upload,
  FileText,
  LayoutDashboard,
  History,
  ShieldCheck,
  Network,
  Target,
} from "lucide-react";
import axios from "axios";
import AnomalyCard from "./components/AnomalyCard";
import AnalysisSkeleton from "./components/AnalysisSkeleton";

function App() {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);

  const onUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setLoading(true);
    const fd = new FormData();
    fd.append("file", file);

    try {
      const res = await axios.post("http://localhost:8000/analyze", fd);
      const findingsWithStatus = res.data.findings.map((f) => ({
        ...f,
        revisado: false,
      }));
      setResults({ ...res.data, findings: findingsWithStatus });
    } catch (err) {
      alert("Error en el motor de IA local");
    } finally {
      setLoading(false);
    }
  };

  const handleFeedback = async (index, finding, isAnomalyReal) => {
    try {
      await axios.post("http://localhost:8000/feedback", {
        document_name: results.document_name,
        patron_texto: finding.patron_detectado,
        score_ia: finding.porcentaje_anomalia,
        es_anomalia_real: isAnomalyReal,
      });

      const updatedFindings = [...results.findings];
      updatedFindings[index].revisado = true;
      setResults({ ...results, findings: updatedFindings });
    } catch (error) {
      console.error("Error al guardar feedback:", error);
    }
  };

  return (
    <div className="min-h-screen flex bg-slate-50">
      <aside className="w-20 border-r border-slate-200 bg-white flex flex-col items-center py-8 gap-8">
        <div className="w-12 h-12 bg-blue-600 rounded-2xl flex items-center justify-center text-white shadow-lg shadow-blue-200">
          <ShieldCheck size={28} />
        </div>
        <nav className="flex flex-col gap-6 text-slate-400">
          <LayoutDashboard className="text-blue-600 cursor-pointer" />
          <History className="hover:text-slate-600 cursor-pointer" />
        </nav>
      </aside>

      <main className="flex-1 p-12 overflow-y-auto">
        <div className="max-w-4xl mx-auto">
          <header className="mb-12 flex justify-between items-end">
            <div>
              <h1 className="text-4xl font-black text-slate-900 tracking-tight">
                PROIA <span className="text-blue-600">Detector</span>
              </h1>
              <p className="text-slate-500 font-medium mt-1">
                Análisis de Integridad con UMAP y TDA Grafos
              </p>
            </div>
            {results && (
              <button
                onClick={() => setResults(null)}
                className="text-sm font-bold text-blue-600 hover:underline"
              >
                Analizar otro archivo
              </button>
            )}
          </header>

          <AnimatePresence mode="wait">
            {!results && !loading ? (
              <motion.label
                key="dropzone"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="group relative flex flex-col items-center justify-center w-full h-80 border-2 border-dashed border-slate-300 rounded-[2.5rem] bg-white hover:border-blue-400 hover:bg-blue-50/30 cursor-pointer transition-all"
              >
                <div className="bg-blue-50 p-6 rounded-full mb-4 group-hover:scale-110 transition-transform">
                  <Upload className="text-blue-600" size={32} />
                </div>
                <span className="text-xl font-bold text-slate-700">
                  Arrastra tu TDR aquí
                </span>
                <span className="text-slate-400 mt-2 text-sm">
                  Formatos soportados: PDF, DOCX
                </span>
                <input
                  type="file"
                  className="hidden"
                  onChange={onUpload}
                  accept=".pdf"
                />
              </motion.label>
            ) : loading ? (
              <motion.div
                key="loading"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <div className="flex flex-col items-center justify-center py-8 gap-4 mb-8">
                  <div className="animate-spin rounded-full h-10 w-10 border-4 border-blue-600 border-t-transparent shadow-lg" />
                  <div className="text-center">
                    <span className="font-bold text-slate-700 text-lg block">
                      Generando proyecciones UMAP y Grafos...
                    </span>
                    <span className="text-sm text-slate-500">
                      Evaluando Local Outlier Factor y Topología
                    </span>
                  </div>
                </div>
                <AnalysisSkeleton />
              </motion.div>
            ) : (
              <motion.div
                key="results"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="space-y-6"
              >
                {/* Cabecera del Documento */}
                <div className="bg-blue-900 text-white p-6 rounded-3xl flex justify-between items-center shadow-xl shadow-blue-100">
                  <div className="flex items-center gap-4">
                    <div className="bg-white/20 p-3 rounded-2xl">
                      <FileText />
                    </div>
                    <div>
                      <p className="text-sm text-blue-200 font-bold uppercase tracking-widest">
                        Documento Analizado
                      </p>
                      <h2 className="text-xl font-bold">
                        {results.document_name}
                      </h2>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-4xl font-black">
                      {results.findings.filter((f) => !f.revisado).length}
                    </p>
                    <p className="text-xs font-bold text-blue-200 uppercase">
                      Alertas Pendientes
                    </p>
                  </div>
                </div>

                {/* NUEVA SECCIÓN: Mapas Visuales generados por el Backend */}
                {results.graficos && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8"
                  >
                    <div className="bg-white p-5 rounded-3xl border border-slate-200 shadow-sm flex flex-col items-center">
                      <div className="w-full flex items-center gap-2 mb-2">
                        <Network size={20} className="text-purple-600" />
                        <h3 className="font-bold text-slate-800 text-sm">
                          Topología Estructural (Grafo)
                        </h3>
                      </div>
                      <p className="text-xs text-slate-400 mb-4 w-full text-left">
                        Nodos rojos representan párrafos aislados del contexto
                        principal.
                      </p>
                      <img
                        src={results.graficos.grafo}
                        alt="Grafo TDA"
                        className="w-full object-contain mix-blend-multiply"
                      />
                    </div>

                    <div className="bg-white p-5 rounded-3xl border border-slate-200 shadow-sm flex flex-col items-center">
                      <div className="w-full flex items-center gap-2 mb-2">
                        <Target size={20} className="text-blue-600" />
                        <h3 className="font-bold text-slate-800 text-sm">
                          Espacio Semántico (UMAP)
                        </h3>
                      </div>
                      <p className="text-xs text-slate-400 mb-4 w-full text-left">
                        Proyección 2D. Puntos alejados indican alta
                        especificidad (outliers).
                      </p>
                      <img
                        src={results.graficos.umap}
                        alt="Mapa UMAP"
                        className="w-full object-contain mix-blend-multiply"
                      />
                    </div>
                  </motion.div>
                )}

                {/* Listado de Anomalías */}
                <div className="grid gap-4">
                  {results.findings.map(
                    (f, i) =>
                      !f.revisado && (
                        <AnomalyCard
                          key={i}
                          index={i}
                          finding={f}
                          onApprove={() => handleFeedback(i, f, true)}
                          onReject={() => handleFeedback(i, f, false)}
                        />
                      ),
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </main>
    </div>
  );
}

export default App;
