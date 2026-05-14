import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Upload,
  FileText,
  LayoutDashboard,
  History,
  ShieldCheck,
  Network,
  Target,
  ChevronLeft,
  ChevronRight,
  AlertTriangle,
} from "lucide-react";
import axios from "axios";
import AnomalyCard from "./components/AnomalyCard";
import AnalysisSkeleton from "./components/AnalysisSkeleton";

function App() {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);

  // Control de la Pestaña Activa ('alertas', 'tda', 'umap')
  const [activeTab, setActiveTab] = useState("alertas");

  // Control de Paginación (5 alertas por página)
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 5;

  const onUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setLoading(true);
    const fd = new FormData();
    fd.append("file", file);

    try {
      const res = await axios.post("http://localhost:8000/analyze", fd);

      // Ordenar por nivel de riesgo de mayor a menor
      const sortedFindings = res.data.findings
        .sort((a, b) => b.porcentaje_anomalia - a.porcentaje_anomalia)
        .map((f) => ({ ...f, revisado: false }));

      setResults({ ...res.data, findings: sortedFindings });
      setActiveTab("alertas");
      setCurrentPage(1);
    } catch (err) {
      alert("Error en la comunicación con el motor local");
    } finally {
      setLoading(false);
    }
  };

  const handleFeedback = async (indexInState, finding, isAnomalyReal) => {
    try {
      await axios.post("http://localhost:8000/feedback", {
        document_name: results.document_name,
        patron_texto: finding.patron_detectado,
        score_ia: finding.porcentaje_anomalia,
        es_anomalia_real: isAnomalyReal,
      });

      const updatedFindings = [...results.findings];
      updatedFindings[indexInState].revisado = true;
      setResults({ ...results, findings: updatedFindings });
    } catch (error) {
      console.error("Error al guardar feedback:", error);
    }
  };

  // Filtrar solo las alertas que no han sido revisadas (aprobadas/rechazadas)
  const pendingFindings = results?.findings
    ? results.findings.filter((f) => !f.revisado)
    : [];

  // Calcular índices de paginación basados en alertas pendientes
  const totalPages = Math.ceil(pendingFindings.length / itemsPerPage);
  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentFindingsPage = pendingFindings.slice(
    indexOfFirstItem,
    indexOfLastItem,
  );

  // Ajustar página actual si nos quedamos sin elementos en la página actual debido al feedback
  useEffect(() => {
    if (currentPage > totalPages && totalPages > 0) {
      setCurrentPage(totalPages);
    }
  }, [pendingFindings.length, totalPages, currentPage]);

  return (
    <div className="min-h-screen flex bg-slate-50 font-sans antialiased">
      {/* Sidebar Fijo */}
      <aside className="w-20 border-r border-slate-200 bg-white flex flex-col items-center py-8 gap-8 shrink-0">
        <div className="w-12 h-12 bg-blue-600 rounded-2xl flex items-center justify-center text-white shadow-lg shadow-blue-200">
          <ShieldCheck size={28} />
        </div>
        <nav className="flex flex-col gap-6 text-slate-400">
          <LayoutDashboard className="text-blue-600 cursor-pointer" />
          <History className="hover:text-slate-600 cursor-pointer" />
        </nav>
      </aside>

      {/* Contenedor Principal */}
      <main className="flex-1 p-6 md:p-12 overflow-y-auto">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <header className="mb-8 flex justify-between items-end">
            <div>
              <h1 className="text-4xl font-black text-slate-900 tracking-tight">
                PROIA <span className="text-blue-600">Detector</span>
              </h1>
              <p className="text-slate-500 font-medium mt-1">
                Auditoría Preventiva para Contratación Pública
              </p>
            </div>
            {results && (
              <button
                onClick={() => setResults(null)}
                className="text-sm font-bold text-blue-600 hover:underline bg-blue-50 px-4 py-2 rounded-xl transition-all"
              >
                Analizar nuevo pliego
              </button>
            )}
          </header>

          <AnimatePresence mode="wait">
            {/* 1. Zona de Carga / Dropzone */}
            {!results && !loading ? (
              <motion.label
                key="dropzone"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="group relative flex flex-col items-center justify-center w-full h-80 border-2 border-dashed border-slate-300 rounded-[2.5rem] bg-white hover:border-blue-400 hover:bg-blue-50/30 cursor-pointer transition-all shadow-sm"
              >
                <div className="bg-blue-50 p-6 rounded-full mb-4 group-hover:scale-110 transition-transform">
                  <Upload className="text-blue-600" size={32} />
                </div>
                <span className="text-xl font-bold text-slate-700">
                  Arrastra tu TDR aquí
                </span>
                <span className="text-slate-400 mt-2 text-sm">
                  Formatos soportados: Archivos PDF técnicos
                </span>
                <input
                  type="file"
                  className="hidden"
                  onChange={onUpload}
                  accept=".pdf"
                />
              </motion.label>
            ) : loading ? (
              /* 2. Skeleton Loader de Procesamiento */
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
                      Analizando pliego de contratación...
                    </span>
                    <span className="text-sm text-slate-500">
                      Buscando Red Flags semánticas y aislamientos estructurales
                      locales
                    </span>
                  </div>
                </div>
                <AnalysisSkeleton />
              </motion.div>
            ) : (
              /* 3. Panel de Resultados Completo */
              <motion.div
                key="results"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="space-y-6"
              >
                {/* Resumen Ejecutivo Superior */}
                <div className="bg-slate-900 text-white p-6 md:p-8 rounded-[2.5rem] flex flex-col md:flex-row justify-between items-start md:items-center gap-4 shadow-xl">
                  <div className="flex items-center gap-4">
                    <div className="bg-white/10 p-4 rounded-2xl border border-white/10">
                      <FileText size={28} className="text-blue-400" />
                    </div>
                    <div>
                      <h2 className="text-xl font-bold truncate max-w-xs md:max-w-md">
                        {results.document_name}
                      </h2>
                      <p className="text-blue-400 font-bold text-xs uppercase tracking-wider mt-1">
                        {pendingFindings.length > 0
                          ? `Riesgo Máximo Detectado: ${results.findings[0]?.porcentaje_anomalia}%`
                          : "Pliego sin alertas restrictivas críticas"}
                      </p>
                    </div>
                  </div>
                  <div className="bg-white/5 border border-white/10 px-6 py-3 rounded-2xl text-center self-stretch md:self-auto flex md:flex-col justify-between items-center">
                    <p className="text-3xl font-black text-blue-400">
                      {pendingFindings.length}
                    </p>
                    <p className="text-[10px] font-bold uppercase tracking-widest text-slate-400">
                      Banderas Rojas
                    </p>
                  </div>
                </div>

                {/* MENÚ DE PESTAÑAS (Tabs Navegables y Responsivos) */}
                <div className="flex border-b border-slate-200 gap-2 overflow-x-auto pb-px">
                  <button
                    onClick={() => setActiveTab("alertas")}
                    className={`flex items-center gap-2 px-6 py-3 font-bold text-sm border-b-2 transition-all whitespace-nowrap rounded-t-xl ${
                      activeTab === "alertas"
                        ? "border-blue-600 text-blue-600 bg-blue-50/50"
                        : "border-transparent text-slate-500 hover:text-slate-800 hover:bg-slate-100"
                    }`}
                  >
                    <AlertTriangle size={16} /> Banderas Rojas Gerenciales
                  </button>
                  <button
                    onClick={() => setActiveTab("tda")}
                    className={`flex items-center gap-2 px-6 py-3 font-bold text-sm border-b-2 transition-all whitespace-nowrap rounded-t-xl ${
                      activeTab === "tda"
                        ? "border-purple-600 text-purple-600 bg-purple-50/50"
                        : "border-transparent text-slate-500 hover:text-slate-800 hover:bg-slate-100"
                    }`}
                  >
                    <Network size={16} /> Estructura del Pliego (TDA)
                  </button>
                  <button
                    onClick={() => setActiveTab("umap")}
                    className={`flex items-center gap-2 px-6 py-3 font-bold text-sm border-b-2 transition-all whitespace-nowrap rounded-t-xl ${
                      activeTab === "umap"
                        ? "border-teal-600 text-teal-600 bg-teal-50/50"
                        : "border-transparent text-slate-500 hover:text-slate-800 hover:bg-slate-100"
                    }`}
                  >
                    <Target size={16} /> Mapa de Cláusulas (UMAP)
                  </button>
                </div>

                {/* CONTENIDO INTERACTIVO DE LAS PESTAÑAS */}
                <div className="py-2">
                  <AnimatePresence mode="wait">
                    {/* Pestaña 1: Alertas y Paginación */}
                    {activeTab === "alertas" && (
                      <motion.div
                        key="tab-alertas"
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="space-y-4"
                      >
                        {currentFindingsPage.length === 0 ? (
                          <div className="bg-white p-12 text-center rounded-3xl border border-slate-200">
                            <ShieldCheck
                              className="text-emerald-500 mx-auto mb-2"
                              size={40}
                            />
                            <p className="font-bold text-slate-700 text-lg">
                              ¡Revisión Completada!
                            </p>
                            <p className="text-slate-400 text-sm mt-1">
                              No quedan banderas rojas pendientes por auditar en
                              este documento.
                            </p>
                          </div>
                        ) : (
                          <>
                            {/* Renderizado de Tarjetas de Anomalías por Página */}
                            <div className="grid gap-4">
                              {currentFindingsPage.map((f) => {
                                // Encontrar el índice absoluto real en la matriz original para el callback del feedback
                                const absoluteIndex =
                                  results.findings.findIndex(
                                    (item) =>
                                      item.patron_detectado ===
                                      f.patron_detectado,
                                  );
                                return (
                                  <AnomalyCard
                                    key={f.patron_detectado}
                                    index={absoluteIndex}
                                    finding={f}
                                    onApprove={() =>
                                      handleFeedback(absoluteIndex, f, true)
                                    }
                                    onReject={() =>
                                      handleFeedback(absoluteIndex, f, false)
                                    }
                                  />
                                );
                              })}
                            </div>

                            {/* Controles Dinámicos de Paginación */}
                            {totalPages > 1 && (
                              <div className="flex items-center justify-between bg-white px-6 py-4 rounded-2xl border border-slate-200 mt-6 shadow-sm">
                                <span className="text-xs font-bold text-slate-500">
                                  Mostrando página{" "}
                                  <strong className="text-slate-800">
                                    {currentPage}
                                  </strong>{" "}
                                  de{" "}
                                  <strong className="text-slate-800">
                                    {totalPages}
                                  </strong>{" "}
                                  ({pendingFindings.length} alertas totales)
                                </span>
                                <div className="flex gap-2">
                                  <button
                                    onClick={() =>
                                      setCurrentPage((prev) =>
                                        Math.max(prev - 1, 1),
                                      )
                                    }
                                    disabled={currentPage === 1}
                                    className="p-2 border border-slate-200 rounded-xl hover:bg-slate-50 transition-all disabled:opacity-40 disabled:hover:bg-transparent"
                                  >
                                    <ChevronLeft size={18} />
                                  </button>
                                  <button
                                    onClick={() =>
                                      setCurrentPage((prev) =>
                                        Math.min(prev + 1, totalPages),
                                      )
                                    }
                                    disabled={currentPage === totalPages}
                                    className="p-2 border border-slate-200 rounded-xl hover:bg-slate-50 transition-all disabled:opacity-40 disabled:hover:bg-transparent"
                                  >
                                    <ChevronRight size={18} />
                                  </button>
                                </div>
                              </div>
                            )}
                          </>
                        )}
                      </motion.div>
                    )}

                    {/* Pestaña 2: Visualización TDA Grafo */}
                    {activeTab === "tda" && results.graficos && (
                      <motion.div
                        key="tab-tda"
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="bg-white p-6 md:p-8 rounded-[2.5rem] border border-slate-200 shadow-sm flex flex-col items-center"
                      >
                        <div className="w-full mb-4">
                          <h3 className="font-black text-slate-800 text-lg flex items-center gap-2">
                            <Network size={20} className="text-purple-600" />{" "}
                            Mapa de Relaciones Topológicas (TDA)
                          </h3>
                          <p className="text-xs text-slate-400 mt-1">
                            Representación de la red del pliego. Los **nodos
                            rojos aislados** representan párrafos sembrados o
                            especificaciones exageradas que se alejan de la
                            consistencia del contrato.
                          </p>
                        </div>
                        <div className="w-full border border-slate-100 rounded-2xl bg-slate-50/50 p-4 flex justify-center">
                          <img
                            src={results.graficos.grafo}
                            alt="Estructura de Red TDA"
                            className="max-h-[400px] w-full object-contain mix-blend-multiply"
                          />
                        </div>
                      </motion.div>
                    )}

                    {/* Pestaña 3: Visualización UMAP Espacio Semántico */}
                    {activeTab === "umap" && results.graficos && (
                      <motion.div
                        key="tab-umap"
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="bg-white p-6 md:p-8 rounded-[2.5rem] border border-slate-200 shadow-sm flex flex-col items-center"
                      >
                        <div className="w-full mb-4">
                          <h3 className="font-black text-slate-800 text-lg flex items-center gap-2">
                            <Target size={20} className="text-teal-600" />{" "}
                            Distribución de Cláusulas (UMAP)
                          </h3>
                          <p className="text-xs text-slate-400 mt-1">
                            Proyección semántica bidimensional. Las agrupaciones
                            densas indican lenguaje normativo estándar; los
                            puntos dispersos en color cálido son cláusulas con
                            requisitos sospechosamente atípicos.
                          </p>
                        </div>
                        <div className="w-full border border-slate-100 rounded-2xl bg-slate-50/50 p-4 flex justify-center">
                          <img
                            src={results.graficos.umap}
                            alt="Espacio Vectorial UMAP"
                            className="max-h-[400px] w-full object-contain mix-blend-multiply"
                          />
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
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
