import React from 'react';
import { ShieldCheck, FileText, Cpu, Lock, Zap, Award } from 'lucide-react';

export default function ScoreCard({ score = 0, summaryData = {}, pagesCrawled = 0, targetUrl = '' }) {
  const getScoreColor = (s) => {
    if (s >= 90) return 'text-emerald-400 stroke-emerald-400 bg-emerald-500/10 border-emerald-500/30';
    if (s >= 75) return 'text-blue-400 stroke-blue-400 bg-blue-500/10 border-blue-500/30';
    if (s >= 50) return 'text-amber-400 stroke-amber-400 bg-amber-500/10 border-amber-500/30';
    return 'text-rose-400 stroke-rose-400 bg-rose-500/10 border-rose-500/30';
  };

  const getScoreBadge = (s) => {
    if (s >= 90) return { label: 'Excellent', color: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40' };
    if (s >= 75) return { label: 'Good', color: 'bg-blue-500/20 text-blue-300 border-blue-500/40' };
    if (s >= 50) return { label: 'Fair', color: 'bg-amber-500/20 text-amber-300 border-amber-500/40' };
    return { label: 'Needs Improvement', color: 'bg-rose-500/20 text-rose-300 border-rose-500/40' };
  };

  const badge = getScoreBadge(score);
  const sectionScores = summaryData?.section_scores || { on_page: 80, technical: 75, security: 100, performance: 70 };
  const grade = summaryData?.grade || 'B';

  const strokeDashoffset = 283 - (283 * score) / 100;

  return (
    <div className="w-full bg-slate-900/90 border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-2xl space-y-8">
      <div className="flex flex-col md:flex-row items-center justify-between gap-8 pb-6 border-b border-slate-800">
        
        {/* Score Gauge Circle */}
        <div className="flex flex-col sm:flex-row items-center gap-6">
          <div className="relative w-36 h-36 flex items-center justify-center">
            <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
              <circle
                cx="50"
                cy="50"
                r="45"
                className="stroke-slate-800"
                strokeWidth="8"
                fill="transparent"
              />
              <circle
                cx="50"
                cy="50"
                r="45"
                className={`transition-all duration-1000 ease-out ${getScoreColor(score)}`}
                strokeWidth="8"
                strokeDasharray="283"
                strokeDashoffset={strokeDashoffset}
                strokeLinecap="round"
                fill="transparent"
              />
            </svg>
            <div className="absolute flex flex-col items-center justify-center text-center">
              <span className="text-4xl font-extrabold text-white tracking-tight">{score}</span>
              <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Out of 100</span>
            </div>
          </div>

          <div className="space-y-2 text-center sm:text-left">
            <div className="flex items-center gap-2 justify-center sm:justify-start">
              <span className={`px-3 py-1 text-xs font-bold rounded-full border ${badge.color}`}>
                {badge.label}
              </span>
              <span className="px-2.5 py-0.5 text-xs font-semibold bg-slate-800 text-slate-300 rounded-md border border-slate-700 flex items-center gap-1">
                <Award className="w-3.5 h-3.5 text-amber-400" />
                Grade {grade}
              </span>
            </div>
            <h2 className="text-2xl font-bold text-white tracking-tight">{targetUrl}</h2>
            <p className="text-xs text-slate-400 flex items-center justify-center sm:justify-start gap-1">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              Automated Audit across <span className="font-semibold text-slate-200">{pagesCrawled}</span> crawled pages
            </p>
          </div>
        </div>

        {/* Severity Metrics Pill */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 w-full md:w-auto">
          <div className="p-3 bg-rose-500/10 border border-rose-500/20 rounded-2xl text-center">
            <span className="block text-2xl font-bold text-rose-400">{summaryData?.severity_counts?.CRITICAL || 0}</span>
            <span className="text-[10px] font-semibold text-rose-300 uppercase tracking-wider">Critical</span>
          </div>
          <div className="p-3 bg-amber-500/10 border border-amber-500/20 rounded-2xl text-center">
            <span className="block text-2xl font-bold text-amber-400">{summaryData?.severity_counts?.HIGH || 0}</span>
            <span className="text-[10px] font-semibold text-amber-300 uppercase tracking-wider">High</span>
          </div>
          <div className="p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-2xl text-center">
            <span className="block text-2xl font-bold text-yellow-400">{summaryData?.severity_counts?.MEDIUM || 0}</span>
            <span className="text-[10px] font-semibold text-yellow-300 uppercase tracking-wider">Medium</span>
          </div>
          <div className="p-3 bg-blue-500/10 border border-blue-500/20 rounded-2xl text-center">
            <span className="block text-2xl font-bold text-blue-400">{summaryData?.severity_counts?.LOW || 0}</span>
            <span className="text-[10px] font-semibold text-blue-300 uppercase tracking-wider">Low</span>
          </div>
        </div>
      </div>

      {/* Section Performance Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-4 bg-slate-800/50 border border-slate-700/60 rounded-2xl space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium flex items-center gap-1.5 text-slate-300">
              <FileText className="w-4 h-4 text-blue-400" /> On-Page SEO
            </span>
            <span className="text-sm font-bold text-white">{sectionScores.on_page}/100</span>
          </div>
          <div className="w-full bg-slate-900 h-2 rounded-full overflow-hidden">
            <div className="bg-blue-500 h-full rounded-full" style={{ width: `${sectionScores.on_page}%` }} />
          </div>
        </div>

        <div className="p-4 bg-slate-800/50 border border-slate-700/60 rounded-2xl space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium flex items-center gap-1.5 text-slate-300">
              <Cpu className="w-4 h-4 text-indigo-400" /> Technical SEO
            </span>
            <span className="text-sm font-bold text-white">{sectionScores.technical}/100</span>
          </div>
          <div className="w-full bg-slate-900 h-2 rounded-full overflow-hidden">
            <div className="bg-indigo-500 h-full rounded-full" style={{ width: `${sectionScores.technical}%` }} />
          </div>
        </div>

        <div className="p-4 bg-slate-800/50 border border-slate-700/60 rounded-2xl space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium flex items-center gap-1.5 text-slate-300">
              <Lock className="w-4 h-4 text-emerald-400" /> Security
            </span>
            <span className="text-sm font-bold text-white">{sectionScores.security}/100</span>
          </div>
          <div className="w-full bg-slate-900 h-2 rounded-full overflow-hidden">
            <div className="bg-emerald-500 h-full rounded-full" style={{ width: `${sectionScores.security}%` }} />
          </div>
        </div>

        <div className="p-4 bg-slate-800/50 border border-slate-700/60 rounded-2xl space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium flex items-center gap-1.5 text-slate-300">
              <Zap className="w-4 h-4 text-amber-400" /> Performance
            </span>
            <span className="text-sm font-bold text-white">{sectionScores.performance}/100</span>
          </div>
          <div className="w-full bg-slate-900 h-2 rounded-full overflow-hidden">
            <div className="bg-amber-500 h-full rounded-full" style={{ width: `${sectionScores.performance}%` }} />
          </div>
        </div>
      </div>
    </div>
  );
}
