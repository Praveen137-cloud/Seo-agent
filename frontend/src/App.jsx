import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Audit from './pages/Audit';
import { ThemeProvider } from './context/ThemeContext';

export default function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 flex flex-col font-sans transition-colors duration-200">
          <Navbar />
          <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/audit/:id" element={<Audit />} />
            </Routes>
          </main>
          <footer className="border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900/90 py-6 text-center text-xs text-slate-500 dark:text-slate-400 font-medium transition-colors">
            <p>© {new Date().getFullYear()} SEOAgent.ai — Professional Website Analysis & Technical Audit Intelligence.</p>
          </footer>
        </div>
      </BrowserRouter>
    </ThemeProvider>
  );
}
