import React, { useState } from 'react';
import { AlertOctagon, AlertTriangle, Info, ChevronDown, ChevronUp, ExternalLink, Filter } from 'lucide-react';

export default function IssueList({ issues = [] }) {
  const [selectedSeverity, setSelectedSeverity] = useState('ALL');
  const [selectedCategory, setSelectedCategory] = useState('ALL');
  const [expandedId, setExpandedId] = useState(null);

  const getSeverityBadge = (severity) => {
    switch (severity.toUpperCase()) {
      case 'CRITICAL':
        return { label: 'CRITICAL', color: 'bg-red-100 dark:bg-red-950/60 text-red-700 dark:text-red-300 border-red-300 dark:border-red-800', icon: AlertOctagon };
      case 'HIGH':
        return { label: 'HIGH', color: 'bg-amber-100 dark:bg-amber-950/60 text-amber-800 dark:text-amber-300 border-amber-300 dark:border-amber-800', icon: AlertTriangle };
      case 'MEDIUM':
        return { label: 'MEDIUM', color: 'bg-yellow-100 dark:bg-yellow-950/60 text-yellow-800 dark:text-yellow-300 border-yellow-300 dark:border-yellow-800', icon: AlertTriangle };
      default:
        return { label: 'LOW', color: 'bg-blue-100 dark:bg-blue-950/60 text-blue-700 dark:text-blue-300 border-blue-300 dark:border-blue-800', icon: Info };
    }
  };

  const filteredIssues = issues.filter(iss => {
    const matchesSev = selectedSeverity === 'ALL' || iss.severity.toUpperCase() === selectedSeverity;
    const matchesCat = selectedCategory === 'ALL' || iss.category.toLowerCase() === selectedCategory.toLowerCase();
    return matchesSev && matchesCat;
  });

  return (
    <div className="w-full bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 sm:p-8 shadow-lg space-y-6 transition-colors">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-slate-200 dark:border-slate-800">
        <div>
          <h3 className="text-xl font-bold text-slate-900 dark:text-white flex items-center gap-2">
            Detected SEO Issues
            <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-red-100 dark:bg-red-950/40 text-red-700 dark:text-red-400 border border-red-200 dark:border-red-800">
              {filteredIssues.length} found
            </span>
          </h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5 font-medium">Filter findings by severity level or category</p>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-2">
          <div className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-100 dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 text-xs text-slate-700 dark:text-slate-300">
            <Filter className="w-3.5 h-3.5 text-slate-500 dark:text-slate-400" />
            <select
              value={selectedSeverity}
              onChange={(e) => setSelectedSeverity(e.target.value)}
              className="bg-transparent text-slate-800 dark:text-slate-200 font-semibold focus:outline-none cursor-pointer"
            >
              <option value="ALL" className="dark:bg-slate-800 dark:text-slate-200">All Severities</option>
              <option value="CRITICAL" className="dark:bg-slate-800 dark:text-slate-200">Critical</option>
              <option value="HIGH" className="dark:bg-slate-800 dark:text-slate-200">High</option>
              <option value="MEDIUM" className="dark:bg-slate-800 dark:text-slate-200">Medium</option>
              <option value="LOW" className="dark:bg-slate-800 dark:text-slate-200">Low</option>
            </select>
          </div>

          <div className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-100 dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 text-xs text-slate-700 dark:text-slate-300">
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="bg-transparent text-slate-800 dark:text-slate-200 font-semibold focus:outline-none cursor-pointer"
            >
              <option value="ALL" className="dark:bg-slate-800 dark:text-slate-200">All Categories</option>
              <option value="on_page" className="dark:bg-slate-800 dark:text-slate-200">On-Page SEO</option>
              <option value="technical" className="dark:bg-slate-800 dark:text-slate-200">Technical</option>
              <option value="security" className="dark:bg-slate-800 dark:text-slate-200">Security</option>
              <option value="performance" className="dark:bg-slate-800 dark:text-slate-200">Performance</option>
            </select>
          </div>
        </div>
      </div>

      {filteredIssues.length === 0 ? (
        <div className="text-center py-12 border border-dashed border-slate-300 dark:border-slate-700 rounded-2xl bg-slate-50 dark:bg-slate-850/40">
          <Info className="w-8 h-8 text-slate-400 dark:text-slate-500 mx-auto mb-2" />
          <p className="text-sm font-medium text-slate-600 dark:text-slate-400">No issues found matching the selected filters.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredIssues.map((issue) => {
            const sevBadge = getSeverityBadge(issue.severity);
            const SevIcon = sevBadge.icon;
            const isExpanded = expandedId === issue.id;

            return (
              <div
                key={issue.id}
                className="bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700/80 rounded-2xl overflow-hidden hover:border-red-300 dark:hover:border-red-500/50 transition-all"
              >
                <button
                  onClick={() => setExpandedId(isExpanded ? null : issue.id)}
                  className="w-full p-4 text-left flex items-start justify-between gap-4 focus:outline-none cursor-pointer"
                >
                  <div className="flex items-start gap-3">
                    <span className={`px-2.5 py-1 text-[10px] font-extrabold rounded-lg border shrink-0 flex items-center gap-1 mt-0.5 ${sevBadge.color}`}>
                      <SevIcon className="w-3 h-3" />
                      {sevBadge.label}
                    </span>

                    <div>
                      <h4 className="text-base font-bold text-slate-900 dark:text-white leading-snug">{issue.title}</h4>
                      <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 font-medium line-clamp-1">{issue.description}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 shrink-0">
                    <span className="text-[11px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider hidden sm:inline">
                      {issue.category.replace('_', ' ')}
                    </span>
                    {isExpanded ? (
                      <ChevronUp className="w-5 h-5 text-slate-500 dark:text-slate-400" />
                    ) : (
                      <ChevronDown className="w-5 h-5 text-slate-500 dark:text-slate-400" />
                    )}
                  </div>
                </button>

                {isExpanded && (
                  <div className="px-4 pb-4 pt-2 border-t border-slate-200 dark:border-slate-700/80 bg-white dark:bg-slate-900/90 space-y-4">
                    <div className="space-y-1">
                      <span className="text-xs font-bold text-slate-700 dark:text-slate-300">Detailed Description:</span>
                      <p className="text-sm text-slate-700 dark:text-slate-300">{issue.description}</p>
                    </div>

                    {issue.page_url && (
                      <div className="flex items-center gap-2 text-xs text-red-700 dark:text-red-300 bg-red-50 dark:bg-red-950/40 p-2.5 rounded-xl border border-red-200 dark:border-red-900">
                        <ExternalLink className="w-4 h-4 shrink-0 text-red-600 dark:text-red-400" />
                        <span className="font-bold text-slate-800 dark:text-slate-200 shrink-0">Affected URL:</span>
                        <a href={issue.page_url} target="_blank" rel="noopener noreferrer" className="hover:underline font-semibold truncate text-red-600 dark:text-red-400">
                          {issue.page_url}
                        </a>
                      </div>
                    )}

                    {issue.evidence && (
                      <div className="p-3 bg-slate-100 dark:bg-slate-800/80 rounded-xl border border-slate-200 dark:border-slate-700 space-y-1">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-bold text-slate-800 dark:text-slate-200 block">Verified Audit Evidence:</span>
                          <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-100 dark:bg-emerald-950/60 text-emerald-800 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800">
                            {issue.verification_status || 'verified'}
                          </span>
                        </div>
                        <p className="text-xs font-mono text-slate-700 dark:text-slate-300 break-all">{issue.evidence}</p>
                      </div>
                    )}

                    {issue.recommendation_summary && (
                      <div className="p-3 bg-emerald-50 dark:bg-emerald-950/40 rounded-xl border border-emerald-200 dark:border-emerald-800 space-y-1">
                        <span className="text-xs font-bold text-emerald-800 dark:text-emerald-300 block">Recommended Quick Fix:</span>
                        <p className="text-xs text-emerald-900 dark:text-emerald-200 font-medium">{issue.recommendation_summary}</p>
                      </div>
                    )}

                    {issue.impact && (
                      <div className="p-3 bg-amber-50 dark:bg-amber-950/40 rounded-xl border border-amber-200 dark:border-amber-800 space-y-1">
                        <span className="text-xs font-bold text-amber-800 dark:text-amber-300 block">SEO & Ranking Impact:</span>
                        <p className="text-xs text-amber-900 dark:text-amber-200 font-medium">{issue.impact}</p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
