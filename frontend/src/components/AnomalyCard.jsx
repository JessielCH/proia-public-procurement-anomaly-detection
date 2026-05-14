import React from "react";
import { motion } from "framer-motion";
import {
  AlertCircle,
  Check,
  X,
  Info,
  ShieldAlert,
  Network,
} from "lucide-react";

const AnomalyCard = ({ finding, onApprove, onReject, index }) => {
  // Detectar el tipo de anomalía basado en la explicación del backend
  const isDireccionamiento =
    finding.explicacion_breve.includes("DIRECCIONAMIENTO");
  const isAislada = finding.explicacion_breve.includes("Aislada");

  // Nivel de severidad
  const isCritical = finding.porcentaje_anomalia > 75 || isDireccionamiento;

  // Configuración visual dinámica según el tipo de hallazgo
  const CardStyle = isDireccionamiento
    ? {
        border: "border-red-500",
        bgIcon: "bg-red-100 text-red-600",
        textColor: "text-red-600",
        title: "Posible Direccionamiento",
        icon: <ShieldAlert size={20} />,
      }
    : isAislada
      ? {
          border: "border-purple-500",
          bgIcon: "bg-purple-100 text-purple-600",
          textColor: "text-purple-600",
          title: "Nodo Semántico Aislado",
          icon: <Network size={20} />,
        }
      : {
          border: isCritical ? "border-amber-500" : "border-blue-500",
          bgIcon: isCritical
            ? "bg-amber-50 text-amber-600"
            : "bg-blue-50 text-blue-600",
          textColor: isCritical ? "text-amber-600" : "text-blue-600",
          title: "Inconsistencia de Patrón",
          icon: <AlertCircle size={20} />,
        };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      className={`group relative bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-sm hover:shadow-md transition-all`}
    >
      {/* Barra lateral de severidad dinámica */}
      <div
        className={`absolute left-0 top-0 bottom-0 w-1.5 ${CardStyle.border.replace("border-", "bg-")}`}
      />

      <div className="p-6">
        <div className="flex justify-between items-start mb-4">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-lg ${CardStyle.bgIcon}`}>
              {CardStyle.icon}
            </div>
            <div>
              <h3
                className={`font-bold text-lg ${isDireccionamiento ? "text-red-700" : "text-slate-800"}`}
              >
                {CardStyle.title}
              </h3>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-[10px] text-slate-500 font-bold uppercase tracking-wider bg-slate-100 px-2 py-0.5 rounded-md">
                  Hallazgo #{index + 1}
                </span>
                {isDireccionamiento && (
                  <span className="text-[10px] text-red-600 font-bold uppercase tracking-wider bg-red-50 px-2 py-0.5 rounded-md border border-red-100">
                    Alta Especificidad
                  </span>
                )}
              </div>
            </div>
          </div>
          <div className="text-right">
            <div className={`text-2xl font-black ${CardStyle.textColor}`}>
              {finding.porcentaje_anomalia}%
            </div>
            <p className="text-[10px] text-slate-400 font-bold uppercase">
              Score Híbrido
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
          <span
            className={isDireccionamiento ? "font-medium text-red-700" : ""}
          >
            {finding.explicacion_breve}
          </span>
        </p>

        <div className="flex items-center justify-between pt-4 border-t border-slate-100">
          <div className="flex items-center gap-2 text-xs font-bold text-slate-500 bg-slate-100 px-3 py-1.5 rounded-full">
            <Network size={14} className="text-slate-400" />
            NODO / PÁRRAFO:{" "}
            {finding.parrafos_afectados.map((p) => `#${p}`).join(", ")}
          </div>

          <div className="flex gap-2">
            <button
              onClick={onReject}
              className="p-2.5 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-xl transition-all"
              title="Descartar falso positivo"
            >
              <X size={20} />
            </button>
            <button
              onClick={onApprove}
              className={`flex items-center gap-2 px-5 py-2.5 text-white rounded-xl transition-all font-semibold text-sm shadow-sm
                ${isDireccionamiento ? "bg-red-600 hover:bg-red-700" : "bg-slate-900 hover:bg-slate-800"}`}
            >
              Confirmar <Check size={16} />
            </button>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default AnomalyCard;
