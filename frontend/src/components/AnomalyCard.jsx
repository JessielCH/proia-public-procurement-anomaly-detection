import React from "react";
import { motion } from "framer-motion";
import { AlertCircle, Check, X, Info, ChevronRight } from "lucide-react";

const AnomalyCard = ({ finding, onApprove, onReject, index }) => {
  const isCritical = finding.porcentaje_anomalia > 75;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      className="group relative bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-sm hover:shadow-md transition-all"
    >
      {/* Barra lateral de severidad */}
      <div
        className={`absolute left-0 top-0 bottom-0 w-1.5 ${isCritical ? "bg-red-500" : "bg-amber-500"}`}
      />

      <div className="p-6">
        <div className="flex justify-between items-start mb-4">
          <div className="flex items-center gap-3">
            <div
              className={`p-2 rounded-lg ${isCritical ? "bg-red-50 text-red-600" : "bg-amber-50 text-amber-600"}`}
            >
              <AlertCircle size={20} />
            </div>
            <div>
              <h3 className="font-bold text-slate-800 text-lg">
                Patrón Inconsistente
              </h3>
              <p className="text-xs text-slate-500 font-medium uppercase tracking-wider">
                Hallazgo #{index + 1}
              </p>
            </div>
          </div>
          <div className="text-right">
            <div
              className={`text-2xl font-black ${isCritical ? "text-red-600" : "text-amber-600"}`}
            >
              {finding.porcentaje_anomalia}%
            </div>
            <p className="text-[10px] text-slate-400 font-bold uppercase">
              Anomalía
            </p>
          </div>
        </div>

        <div className="bg-slate-50 border border-slate-100 rounded-xl p-4 mb-4 relative">
          <p className="text-slate-700 italic text-sm leading-relaxed">
            "{finding.patron_detectado}"
          </p>
          <div className="absolute -right-2 -top-2 bg-white border border-slate-200 p-1 rounded-full shadow-sm text-slate-400">
            <Info size={14} />
          </div>
        </div>

        <p className="text-slate-600 text-sm mb-6 flex gap-2">
          <span className="font-semibold text-slate-800 shrink-0">
            Análisis:
          </span>
          {finding.explicacion_breve}
        </p>

        <div className="flex items-center justify-between pt-4 border-t border-slate-100">
          <div className="flex items-center gap-2 text-xs font-bold text-slate-400 bg-slate-50 px-3 py-1.5 rounded-full">
            PÁRRAFOS:{" "}
            {finding.parrafos_afectados.map((p) => `#${p}`).join(", ")}
          </div>

          <div className="flex gap-2">
            <button
              onClick={onReject}
              className="p-2.5 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-xl transition-all"
              title="Rechazar hallazgo"
            >
              <X size={20} />
            </button>
            <button
              onClick={onApprove}
              className="flex items-center gap-2 px-5 py-2.5 bg-slate-900 text-white rounded-xl hover:bg-slate-800 transition-all font-semibold text-sm shadow-sm"
            >
              Aprobar <Check size={16} />
            </button>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default AnomalyCard;
