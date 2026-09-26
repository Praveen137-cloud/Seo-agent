import React, { useState } from 'react';
import { AlertOctagon, AlertTriangle, Info, ChevronDown, ChevronUp, ExternalLink, Filter } from 'lucide-react';

export default function IssueList({ issues = [] }) {
  const [selectedSeverity, setSelectedSeverity] = useState('ALL');
  const [selectedCategory, setSelectedCategory] = useState('ALL');
  const [expandedId, setExpandedId] = useState(null);

  const getSeverityBadge = (severity) => {
    switch (severity.toUpperCase()) {
      case 'CRITICAL':
        return { label: 'CRITICAL', color: 'bg-red-100 text-red-700 border-red-300', icon: AlertOctagon };
      case 'HIGH':
        return { label: 'HIGH', color: 'bg-amber-100 text-amber-800 border-amber-300', icon: AlertTriangle };
      case 'MEDIUM':
        return { label: 'MEDIUM', color: 'bg-yellow-100 text-yellow-800 border-yellow-300', icon: AlertTriangle };
      default:
        return { label: 'LOW', color: 'bg-blue-100 text-blue-700 border-blue-300', icon: Info };
    }
  };

  const filteredIssues = issues.filter(iss => {
    const matchesSev = selectedSeverity === 'ALL' || iss.severity.toUpperCase() === selectedSeverity;
    const matchesCat = selectedCategory === 'ALL' || iss.category.toLowerCase() === selectedCategory.toLowerCase();
    return matchesSev && matchesCat;
  });

  return (
    <div className="w-full bg-white border border-slate-200 rounded-3xl p-6 sm:p-8 shadow-lg space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <h3 className="text-xl font-bold text-slate-900 flex items-center gap-2">
            Detected SEO Issues
            <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-red-100 text-red-700 border border-red-200">
              {filteredIssues.length} found
            </span>
          </h3>
          <p className="text-xs text-slate-500 mt-0.5 font-medium">Filter findings by severity level or category</p>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-2">
          <div className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-100 rounded-xl border border-slate-200 text-xs text-slate-700">
            <Filter className="w-3.5 h-3.5 text-slate-500" />
            <select
              value={selectedSeverity}
              onChange={(e) => setSelectedSeverity(e.target.value)}
              className="bg-transparent text-slate-800 font-semibold focus:outline-none cursor-pointer"
            >
              <option value="ALL">All Severities</option>
              <option value="CRITICAL">Critical</option>
              <option value="HIGH">High</option>
              <option value="MEDIUM">Medium</option>
              <option value="LOW">Low</option>
            </select>
          </div>

          <div className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-100 rounded-xl border border-slate-200 text-xs text-slate-700">
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="bg-transparent text-slate-800 font-semibold focus:outline-none cursor-pointer"
            >
              <option value="ALL">All Categories</option>
              <option value="on_page">On-Page SEO</option>
              <option value="technical">Technical</option>
              <option value="security">Security</option>
              <option value="performance">Performance</option>
            </select>
          </div>
        </div>
      </div>

      {filteredIssues.length === 0 ? (
        <div className="text-center py-12 border border-dashed border-slate-300 rounded-2xl bg-slate-50">
          <Info className="w-8 h-8 text-slate-400 mx-auto mb-2" />
          <p className="text-sm font-medium text-slate-600">No issues found matching the selected filters.</p>
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
                className="bg-slate-50 border border-slate-200 rounded-2xl overflow-hidden hover:border-red-300 transition-all"
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
                      <h4 className="text-base font-bold text-slate-900 leading-snug">{issue.title}</h4>
                      <p className="text-xs text-slate-500 mt-1 font-medium line-clamp-1">{issue.description}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 shrink-0">
                    <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider hidden sm:inline">
                      {issue.category.replace('_', ' ')}
                    </span>
                    {isExpanded ? (
                      <ChevronUp className="w-5 h-5 text-slate-500" />
                    ) : (
                      <ChevronDown className="w-5 h-5 text-slate-500" />
                    )}
                  </div>
                </button>

                {isExpanded && (
                  <div className="px-4 pb-4 pt-2 border-t border-slate-200 bg-white space-y-4">
                    <div className="space-y-1">
                      <span className="text-xs font-bold text-slate-700">Detailed Description:</span>
                      <p className="text-sm text-slate-700">{issue.description}</p>
                    </div>

                    {issue.page_url && (
                      <div className="flex items-center gap-2 text-xs text-red-700 bg-red-50 p-2.5 rounded-xl border border-red-200">
                        <ExternalLink className="w-4 h-4 shrink-0 text-red-600" />
                        <span className="font-bold text-slate-800 shrink-0">Affected URL:</span>
                        <a href={issue.page_url} target="_blank" rel="noopener noreferrer" className="hover:underline font-semibold truncate text-red-600">
                          {issue.page_url}
                        </a>
                      </div>
                    )}

                    {issue.recommendation_summary && (
                      <div className="p-3 bg-emerald-50 rounded-xl border border-emerald-200 space-y-1">
                        <span className="text-xs font-bold text-emerald-800 block">Recommended Quick Fix:</span>
                        <p className="text-xs text-emerald-900 font-medium">{issue.recommendation_summary}</p>
                      </div>
                    )}

                    {issue.impact && (
                      <div className="p-3 bg-amber-50 rounded-xl border border-amber-200 space-y-1">
                        <span className="text-xs font-bold text-amber-800 block">SEO & Ranking Impact:</span>
                        <p className="text-xs text-amber-900 font-medium">{issue.impact}</p>
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
