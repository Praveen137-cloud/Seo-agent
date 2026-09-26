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

      {/* 1-Click Browser Integration Section (Extension & Search Shortcut) */}
      <section className="max-w-4xl mx-auto px-4">
        <div className="p-6 sm:p-8 bg-white border border-slate-200 rounded-3xl shadow-lg space-y-6">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-200 pb-4">
            <div className="space-y-1">
              <div className="inline-flex items-center gap-1.5 text-xs font-bold text-red-700 bg-red-50 px-3 py-1 rounded-full border border-red-200">
                <Puzzle className="w-3.5 h-3.5 text-red-600" /> 1-Click Browser Integration
              </div>
              <h3 className="text-xl font-bold text-slate-900">Audit Any Site Instantly While Browsing</h3>
            </div>

            <div className="flex items-center gap-2 bg-slate-100 p-1 rounded-xl border border-slate-200 text-xs font-bold">
              <button
                onClick={() => setActiveTab('extension')}
                className={`px-3 py-1.5 rounded-lg transition-all cursor-pointer ${
                  activeTab === 'extension' ? 'bg-white text-red-600 shadow-xs' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Chrome Extension (100% Reliable)
              </button>
              <button
                onClick={() => setActiveTab('search')}
                className={`px-3 py-1.5 rounded-lg transition-all cursor-pointer ${
                  activeTab === 'search' ? 'bg-white text-red-600 shadow-xs' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Address Bar Shortcut
              </button>
            </div>
          </div>

          {activeTab === 'extension' ? (
            <div className="space-y-4 text-xs text-slate-700 font-medium">
              <p className="leading-relaxed">
                Modern security policies (CSP) block traditional bookmarklets on many HTTPS sites. We built a lightweight <strong>1-Click Chrome/Edge Extension</strong> that bypasses all restrictions!
              </p>

              <div className="bg-slate-50 p-4 rounded-2xl border border-slate-200 space-y-3">
                <span className="font-bold text-slate-900 text-sm block">10-Second Extension Setup Instructions:</span>
                <ol className="list-decimal pl-5 space-y-2 text-slate-700">
                  <li>Open Chrome or Edge and go to <code className="bg-slate-200 px-1.5 py-0.5 rounded text-red-700 font-mono">chrome://extensions</code> (or <code className="bg-slate-200 px-1.5 py-0.5 rounded text-red-700 font-mono">edge://extensions</code>).</li>
                  <li>Enable <strong className="text-slate-900">Developer mode</strong> toggle in the top-right corner.</li>
                  <li>Click <strong className="text-slate-900">Load unpacked</strong> button and select the folder:
                    <div className="mt-1 p-2 bg-slate-900 text-emerald-400 font-mono rounded-xl text-[11px] font-semibold select-all">
                      c:\Users\prave\Downloads\seo agent\chrome-extension
                    </div>
                  </li>
                  <li>Pin the extension icon to your toolbar! Whenever you visit any site, 1-click the icon to audit it instantly!</li>
                </ol>
              </div>
            </div>
          ) : (
            <div className="space-y-4 text-xs text-slate-700 font-medium">
              <p className="leading-relaxed">
                Audit any website straight from your browser address bar by typing <code className="bg-red-100 text-red-700 px-1.5 py-0.5 rounded font-bold font-mono">seo example.com</code>!
              </p>

              <div className="bg-slate-50 p-4 rounded-2xl border border-slate-200 space-y-3">
                <span className="font-bold text-slate-900 text-sm block">How to set up Address Bar Search Shortcut:</span>
                <ol className="list-decimal pl-5 space-y-2 text-slate-700">
                  <li>Go to Chrome Settings → <strong className="text-slate-900">Search engine</strong> → <strong className="text-slate-900">Manage search engines and site search</strong>.</li>
                  <li>Under <strong>Site search</strong>, click <strong>Add</strong>.</li>
                  <li>Fill in:
                    <ul className="list-disc pl-5 mt-1 space-y-1 font-mono text-[11px]">
                      <li>Shortcut: <strong className="text-red-600">seo</strong></li>
                      <li>URL with %s in place of query: <strong className="text-emerald-700">http://localhost:5173/?url=%s</strong></li>
                    </ul>
                  </li>
                  <li>Now type <code className="bg-slate-200 px-1.5 py-0.5 rounded font-mono font-bold">seo github.com</code> in your URL bar anytime to launch an instant audit!</li>
                </ol>
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
