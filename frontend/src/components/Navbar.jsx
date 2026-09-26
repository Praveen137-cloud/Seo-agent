import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { FileText } from 'lucide-react';

export default function Navbar() {
  const location = useLocation();

  return (
    <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-md border-b border-slate-200 shadow-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-3 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-red-600 via-rose-600 to-red-500 flex items-center justify-center shadow-md shadow-red-600/20 group-hover:scale-105 transition-transform">
            <FileText className="w-5 h-5 text-white" />
          </div>
          <div>
            <span className="font-extrabold text-xl text-slate-900 tracking-tight flex items-center gap-1">
              SEO<span className="text-red-600">Agent</span>.ai
            </span>
            <span className="block text-[10px] text-slate-500 font-semibold tracking-wider uppercase">
              Website Analysis & Recommendations
            </span>
          </div>
        </Link>

        <nav className="flex items-center gap-6">
          <Link
            to="/"
            className={`text-sm font-semibold transition-colors ${
              location.pathname === '/' ? 'text-red-600 font-bold' : 'text-slate-600 hover:text-red-600'
            }`}
          >
            Dashboard
          </Link>
          
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-50 border border-emerald-200 text-xs font-semibold text-emerald-700">
            <span className="w-2 h-2 rounded-full bg-emerald-600 animate-pulse" />
            <span>Engine Active</span>
          </div>
        </nav>
      </div>
    </header>
  );
}
