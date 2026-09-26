import React from 'react';
import { Search, ShieldAlert, Cpu, CheckCircle2, Loader2 } from 'lucide-react';

const STAGES = [
  { key: 'pending', label: 'Queued', icon: Search },
  { key: 'crawling', label: 'Crawling Site', icon: Search },
  { key: 'analyzing', label: 'Analyzing SEO Factors', icon: Cpu },
  { key: 'scoring', label: 'Calculating Scores', icon: ShieldAlert },
  { key: 'ai_processing', label: 'Generating AI Strategy', icon: Cpu },
  { key: 'completed', label: 'Complete', icon: CheckCircle2 }
];

export default function AuditProgress({ status, pagesCrawled = 0, targetUrl = '' }) {
  const getStageIndex = (currentStatus) => {
    const idx = STAGES.findIndex(s => s.key === currentStatus);
    return idx >= 0 ? idx : 1;
  };

  const currentIdx = getStageIndex(status);

  return (
    <div className="w-full max-w-3xl mx-auto p-6 bg-white border border-slate-200 rounded-2xl shadow-xl space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
            <Loader2 className="w-5 h-5 text-red-600 animate-spin" />
            SEO Audit In Progress
          </h3>
          <p className="text-xs text-slate-500 mt-1 font-medium">Analyzing <span className="text-red-600 font-bold">{targetUrl}</span></p>
        </div>
        <div className="text-right">
          <span className="text-xs font-bold px-3 py-1 rounded-full bg-red-100 border border-red-200 text-red-700 capitalize">
            {status.replace('_', ' ')}
          </span>
          {pagesCrawled > 0 && (
            <p className="text-xs text-slate-500 mt-1 font-semibold">{pagesCrawled} pages crawled</p>
          )}
        </div>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden border border-slate-200">
        <div
          className="bg-gradient-to-r from-red-600 to-rose-600 h-full transition-all duration-500 ease-out"
          style={{ width: `${Math.min(100, Math.max(15, ((currentIdx + 1) / STAGES.length) * 100))}%` }}
        />
      </div>

      {/* Stage indicators */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 pt-2">
        {STAGES.slice(1).map((stage, idx) => {
          const isDone = currentIdx > idx + 1;
          const isCurrent = currentIdx === idx + 1;
          const Icon = stage.icon;

          return (
            <div
              key={stage.key}
              className={`p-3 rounded-xl border flex flex-col items-center text-center transition-all ${
                isCurrent
                  ? 'bg-red-50 border-red-300 text-red-700 font-bold shadow-sm scale-105'
                  : isDone
                  ? 'bg-emerald-50 border-emerald-200 text-emerald-700'
                  : 'bg-slate-50 border-slate-200 text-slate-400'
              }`}
            >
              {isDone ? (
                <CheckCircle2 className="w-5 h-5 mb-1 text-emerald-600" />
              ) : isCurrent ? (
                <Loader2 className="w-5 h-5 mb-1 animate-spin text-red-600" />
              ) : (
                <Icon className="w-5 h-5 mb-1 opacity-40" />
              )}
              <span className="text-xs font-bold">{stage.label}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
