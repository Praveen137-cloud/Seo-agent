import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Audit from './pages/Audit';

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans">
        <Navbar />
        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/audit/:id" element={<Audit />} />
          </Routes>
        </main>
        <footer className="border-t border-slate-200 bg-white py-6 text-center text-xs text-slate-500 font-medium">
          <p>© {new Date().getFullYear()} SEOAgent.ai — Professional Website Analysis & Technical Audit Intelligence.</p>
        </footer>
      </div>
    </BrowserRouter>
  );
}
