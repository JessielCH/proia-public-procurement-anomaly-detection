import React from "react";

const AnalysisSkeleton = () => (
  <div className="space-y-6 animate-pulse">
    {[1, 2, 3].map((i) => (
      <div
        key={i}
        className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm"
      >
        <div className="flex justify-between mb-4">
          <div className="h-6 w-1/3 bg-slate-200 rounded"></div>
          <div className="h-8 w-12 bg-slate-200 rounded-full"></div>
        </div>
        <div className="h-20 bg-slate-100 rounded-lg mb-4"></div>
        <div className="flex justify-between">
          <div className="h-4 w-1/4 bg-slate-200 rounded"></div>
          <div className="flex gap-2">
            <div className="h-9 w-24 bg-slate-200 rounded-lg"></div>
            <div className="h-9 w-24 bg-slate-200 rounded-lg"></div>
          </div>
        </div>
      </div>
    ))}
  </div>
);

export default AnalysisSkeleton;
