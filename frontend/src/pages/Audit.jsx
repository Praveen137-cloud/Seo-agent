import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getAuditStatus, getAuditIssues, getAuditRecommendations } from '../services/api';
import AuditProgress from '../components/AuditProgress';
import ScoreCard from '../components/ScoreCard';
import IssueList from '../components/IssueList';
import RecommendationList from '../components/RecommendationList';
import ReportButton from '../components/ReportButton';
import { ArrowLeft, Sparkles, ShieldAlert, Cpu, AlertCircle } from 'lucide-react';

export default function Audit() {
  const { id } = useParams();
  const [audit, setAudit] = useState(null);
  const [issues, setIssues] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('issues');

  useEffect(() => {
    let intervalId = null;

    const fetchAudit = async () => {
      try {
        const data = await getAuditStatus(id);
        setAudit(data);

        if (data.status === 'completed' || data.status === 'failed') {
          if (intervalId) clearInterval(intervalId);
          // Fetch issues & recommendations
          const [issData, recData] = await Promise.all([
            getAuditIssues(id),
            getAuditRecommendations(id)
          ]);
          setIssues(issData);
          setRecommendations(recData);
          setLoading(false);
        }
      } catch (err) {
        console.error('Failed to fetch audit details:', err);
        setLoading(false);
      }
    };

    fetchAudit();

    // Poll status every 3 seconds if not completed
    intervalId = setInterval(fetchAudit, 3000);

    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [id]);

  if (loading && (!audit || audit.status !== 'completed')) {
    return (
      <div className="py-12 space-y-6">
        <Link to="/" className="inline-flex items-center gap-2 text-xs font-bold text-slate-600 hover:text-red-600 transition-colors mb-4">
          <ArrowLeft className="w-4 h-4" /> Back to Dashboard
        </Link>
        <AuditProgress
          status={audit?.status || 'pending'}
          pagesCrawled={audit?.pages_crawled || 0}
          targetUrl={audit?.target_url || ''}
        />
      </div>
    );
  }

  if (audit?.status === 'failed') {
    return (
      <div className="py-12 max-w-xl mx-auto text-center space-y-4">
        <div className="w-12 h-12 rounded-full bg-red-100 border border-red-200 text-red-600 mx-auto flex items-center justify-center">
          <AlertCircle className="w-6 h-6" />
        </div>
        <h2 className="text-xl font-bold text-slate-900">SEO Audit Failed</h2>
        <p className="text-xs text-red-700 bg-red-50 p-4 rounded-xl border border-red-200 font-medium">
          {audit.error_message || 'An unexpected error occurred during the website audit.'}
        </p>
        <Link to="/" className="inline-block px-6 py-2.5 bg-slate-900 text-white font-bold rounded-xl shadow-md">
          Return to Dashboard
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-8 py-6">
      {/* Navigation Top Bar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <Link to="/" className="inline-flex items-center gap-2 text-xs font-bold text-slate-600 hover:text-red-600 transition-colors">
          <ArrowLeft className="w-4 h-4" /> Back to Dashboard
        </Link>

        <ReportButton auditId={id} />
      </div>

      {/* Score Card Header */}
      <ScoreCard
        score={audit?.score || 0}
        summaryData={audit?.summary_data || {}}
        pagesCrawled={audit?.pages_crawled || 0}
        targetUrl={audit?.target_url || ''}
      />

      {/* View Tabs */}
      <div className="flex border-b border-slate-200 gap-6">
        <button
          onClick={() => setActiveTab('issues')}
          className={`pb-3 text-sm font-extrabold flex items-center gap-2 border-b-2 transition-all cursor-pointer ${
            activeTab === 'issues'
              ? 'border-red-600 text-red-600'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <ShieldAlert className="w-4 h-4" />
          Detected Issues ({issues.length})
        </button>

        <button
          onClick={() => setActiveTab('recommendations')}
          className={`pb-3 text-sm font-extrabold flex items-center gap-2 border-b-2 transition-all cursor-pointer ${
            activeTab === 'recommendations'
              ? 'border-red-600 text-red-600'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <Sparkles className="w-4 h-4 text-red-600" />
          AI Recommendations & Content Strategy ({recommendations.length})
        </button>
      </div>

      {/* Tab Panels */}
      {activeTab === 'issues' ? (
        <IssueList issues={issues} />
      ) : (
        <RecommendationList recommendations={recommendations} />
      )}
    </div>
  );
}
