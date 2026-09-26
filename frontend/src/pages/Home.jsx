import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import UrlInput from '../components/UrlInput';
import { startAudit, getRecentAudits } from '../services/api';
import { Sparkles, ShieldCheck, Cpu, ArrowRight, History, Zap, Puzzle, Search, CheckCircle } from 'lucide-react';

export default function Home() {
  const [isLoading, setIsLoading] = useState(false);
  const [recentAudits, setRecentAudits] = useState([]);
  const [activeTab, setActiveTab] = useState('extension');
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  useEffect(() => {
    fetchHistory();
    checkUrlParam();
  }, [searchParams]);

  const fetchHistory = async () => {
    try {
      const data = await getRecentAudits(6);
      setRecentAudits(data);
    } catch (err) {
      console.error('Failed to fetch recent audits:', err);
    }
  };

  const checkUrlParam = () => {
    const urlParam = searchParams.get('url');
    if (urlParam && urlParam.trim()) {
      let target = urlParam.trim();
      if (!target.startsWith('http://') && !target.startsWith('https://')) {
        target = 'https://' + target;
      }
      handleAuditSubmit(target, 25);
    }
  };

  const handleAuditSubmit = async (url, maxPages) => {
    setIsLoading(true);
    try {
      const res = await startAudit(url, maxPages);
      if (res.audit_id) {
        navigate(`/audit/${res.audit_id}`);
      }
    } catch (err) {
      console.error('Error starting audit:', err);
      alert('Failed to start SEO audit. Please check your backend connection.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-12 py-6">
      {/* Hero Section */}
      <section className="text-center space-y-6 max-w-4xl mx-auto px-4">
        <h1 className="text-4xl sm:text-6xl font-black text-slate-900 tracking-tight leading-tight">
          Supercharge Your Website <span className="text-red-600">SEO & Rankings</span>
        </h1>

        <p className="text-slate-600 text-base sm:text-lg max-w-2xl mx-auto font-medium">
          Fast multi-page crawling, technical diagnostics, 0-100 scoring engine, and automated LLM-powered recommendations in seconds.
        </p>

        <div className="pt-2">
          <UrlInput onSubmit={handleAuditSubmit} isLoading={isLoading} />
        </div>
      </section>

      {/* 1-Click Browser Integration Section */}
      <section className="max-w-4xl mx-auto px-4">
        <div className="p-5 sm:p-6 bg-white border border-slate-200 rounded-2xl shadow-sm space-y-4">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-slate-100 pb-3">
            <div className="flex items-center gap-2">
              <span className="p-1.5 bg-red-50 text-red-600 rounded-lg">
                <Puzzle className="w-4 h-4" />
              </span>
              <h3 className="text-base font-bold text-slate-900">Chrome Extension & Shortcut Setup</h3>
            </div>

            <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-lg border border-slate-200 text-xs font-semibold">
              <button
                onClick={() => setActiveTab('extension')}
                className={`px-2.5 py-1 rounded-md transition-all cursor-pointer ${
                  activeTab === 'extension' ? 'bg-white text-red-600 shadow-xs' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Chrome Extension
              </button>
              <button
                onClick={() => setActiveTab('search')}
                className={`px-2.5 py-1 rounded-md transition-all cursor-pointer ${
                  activeTab === 'search' ? 'bg-white text-red-600 shadow-xs' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Address Bar Shortcut
              </button>
            </div>
          </div>

          {activeTab === 'extension' ? (
            <div className="text-xs text-slate-600 space-y-2 font-medium">
              <div className="bg-slate-50 p-3 rounded-xl border border-slate-200 space-y-2">
                <div className="flex items-center gap-2 text-slate-800 font-bold">
                  <CheckCircle className="w-3.5 h-3.5 text-emerald-600" />
                  <span>Quick Chrome Extension Setup:</span>
                </div>
                <ol className="list-decimal pl-5 space-y-1 text-slate-700">
                  <li>In Chrome, open <code className="bg-slate-200 px-1 py-0.5 rounded text-red-700 font-mono">chrome://extensions</code> and enable <strong>Developer mode</strong>.</li>
                  <li>Click <strong>Load unpacked</strong> and select the <code className="bg-slate-200 px-1 py-0.5 rounded font-mono">chrome-extension</code> folder.</li>
                </ol>
              </div>
            </div>
          ) : (
            <div className="text-xs text-slate-600 space-y-2 font-medium">
              <div className="bg-slate-50 p-3 rounded-xl border border-slate-200 space-y-2">
                <div className="flex items-center gap-2 text-slate-800 font-bold">
                  <Search className="w-3.5 h-3.5 text-red-600" />
                  <span>Address Bar Search Shortcut:</span>
                </div>
                <p className="text-slate-700">
                  Add custom site search in Chrome settings with URL pattern: <code className="bg-slate-200 px-1.5 py-0.5 rounded font-mono text-slate-900">https://seo-agent-inky-seven.vercel.app/?url=%s</code>
                </p>
              </div>
            </div>
          )}
        </div>
      </section>

      {/* Feature Highlights Grid */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="p-6 bg-white border border-slate-200 rounded-3xl space-y-3 hover:border-red-300 hover:shadow-xl transition-all">
          <div className="w-12 h-12 rounded-2xl bg-red-100 border border-red-200 flex items-center justify-center text-red-600">
            <Cpu className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-slate-900">Controlled Web Crawler</h3>
          <p className="text-xs text-slate-600 leading-relaxed font-medium">
            Extracts titles, meta descriptions, H1/H2 heading structure, image alt text, and internal links across your domain.
          </p>
        </div>

        <div className="p-6 bg-white border border-slate-200 rounded-3xl space-y-3 hover:border-red-300 hover:shadow-xl transition-all">
          <div className="w-12 h-12 rounded-2xl bg-rose-100 border border-rose-200 flex items-center justify-center text-rose-600">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-slate-900">Technical Diagnostic Engine</h3>
          <p className="text-xs text-slate-600 leading-relaxed font-medium">
            Evaluates HTTPS security, canonical alignment, XML sitemaps, response latency (TTFB), and document payload sizes.
          </p>
        </div>

        <div className="p-6 bg-white border border-slate-200 rounded-3xl space-y-3 hover:border-red-300 hover:shadow-xl transition-all">
          <div className="w-12 h-12 rounded-2xl bg-amber-100 border border-amber-200 flex items-center justify-center text-amber-600">
            <Sparkles className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-slate-900">Ollama AI Strategy & Content</h3>
          <p className="text-xs text-slate-600 leading-relaxed font-medium">
            Translates findings into simple explanations, prioritizes fixes, and generates ready-to-copy meta titles, descriptions, and keywords.
          </p>
        </div>
      </section>

      {/* Recent Audits History */}
      {recentAudits.length > 0 && (
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
              <History className="w-5 h-5 text-red-600" />
              Recent SEO Audits
            </h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {recentAudits.map((audit) => (
              <Link
                key={audit.id}
                to={`/audit/${audit.id}`}
                className="p-5 bg-white border border-slate-200 rounded-2xl hover:border-red-300 hover:shadow-md transition-all flex items-center justify-between group"
              >
                <div className="space-y-1 truncate pr-3">
                  <span className="font-bold text-slate-900 text-sm block truncate group-hover:text-red-600 transition-colors">
                    {audit.target_url}
                  </span>
                  <div className="flex items-center gap-2 text-xs font-medium text-slate-500">
                    <span>{audit.pages_crawled} pages</span>
                    <span>•</span>
                    <span className="capitalize">{audit.status}</span>
                  </div>
                </div>

                <div className="flex items-center gap-3 shrink-0">
                  <div className="text-right">
                    <span className="text-lg font-black text-red-600">{audit.score || 0}</span>
                    <span className="text-[10px] text-slate-400 block font-bold">/ 100</span>
                  </div>
                  <ArrowRight className="w-4 h-4 text-slate-400 group-hover:text-red-600 transition-colors" />
                </div>
              </Link>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
