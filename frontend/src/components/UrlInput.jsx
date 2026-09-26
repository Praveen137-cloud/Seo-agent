import React, { useState } from 'react';
import { Globe, ArrowRight, Layers, AlertCircle } from 'lucide-react';

export default function UrlInput({ onSubmit, isLoading }) {
  const [url, setUrl] = useState('');
  const [maxPages, setMaxPages] = useState(25);
  const [error, setError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');

    let trimmed = url.trim();
    if (!trimmed) {
      setError('Please enter a valid website URL');
      return;
    }

    if (!trimmed.startsWith('http://') && !trimmed.startsWith('https://')) {
      trimmed = 'https://' + trimmed;
    }

    onSubmit(trimmed, maxPages);
  };

  return (
    <div className="w-full max-w-3xl mx-auto">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="relative flex flex-col sm:flex-row items-center gap-2 p-2.5 bg-white border border-slate-200 rounded-2xl shadow-xl hover:shadow-2xl focus-within:border-red-500 transition-all">
          <div className="flex items-center gap-3 px-3 py-2 w-full sm:w-auto flex-1">
            <Globe className="w-6 h-6 text-red-600 shrink-0" />
            <input
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="Enter website URL (e.g. example.com)"
              disabled={isLoading}
              className="w-full bg-transparent text-slate-900 placeholder-slate-400 text-base font-medium focus:outline-none"
            />
          </div>

          <div className="flex items-center gap-3 w-full sm:w-auto px-2 justify-between">
            <div className="flex items-center gap-1.5 text-xs text-slate-600 bg-slate-100 px-3 py-2 rounded-xl border border-slate-200">
              <Layers className="w-4 h-4 text-slate-500" />
              <select
                value={maxPages}
                onChange={(e) => setMaxPages(Number(e.target.value))}
                disabled={isLoading}
                className="bg-transparent text-slate-800 font-semibold focus:outline-none cursor-pointer"
              >
                <option value={10}>10 pages</option>
                <option value={25}>25 pages</option>
                <option value={50}>50 pages</option>
                <option value={100}>100 pages</option>
              </select>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="px-6 py-3.5 bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-700 hover:to-rose-700 text-white font-bold rounded-xl shadow-lg shadow-red-600/25 flex items-center justify-center gap-2 shrink-0 transition-all transform active:scale-95 disabled:opacity-50 cursor-pointer"
            >
              {isLoading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span>Analyzing...</span>
                </>
              ) : (
                <>
                  <span>Audit Website</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </div>
        </div>

        {error && (
          <div className="flex items-center gap-2 text-red-700 text-sm px-4 py-2.5 bg-red-50 border border-red-200 rounded-xl">
            <AlertCircle className="w-4 h-4 shrink-0 text-red-600" />
            <span>{error}</span>
          </div>
        )}
      </form>
    </div>
  );
}
