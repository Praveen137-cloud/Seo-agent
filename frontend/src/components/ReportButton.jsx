import React, { useState } from 'react';
import { Download, Loader2 } from 'lucide-react';
import { getReportDownloadUrl } from '../services/api';

export default function ReportButton({ auditId, disabled = false }) {
  const [isDownloading, setIsDownloading] = useState(false);

  const handleDownload = () => {
    if (!auditId || disabled) return;
    setIsDownloading(true);
    
    const downloadUrl = getReportDownloadUrl(auditId);
    
    // Create an anchor element to trigger download
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.setAttribute('download', `SEO_Audit_Report_${auditId ? auditId.slice(0, 8) : 'download'}.pdf`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    setTimeout(() => {
      setIsDownloading(false);
    }, 2000);
  };

  return (
    <button
      onClick={handleDownload}
      disabled={disabled || isDownloading}
      className="px-5 py-2.5 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold text-xs rounded-xl shadow-lg shadow-emerald-600/20 flex items-center gap-2 transition-all transform active:scale-95 disabled:opacity-50 cursor-pointer border border-emerald-400/20"
    >
      {isDownloading ? (
        <>
          <Loader2 className="w-4 h-4 animate-spin text-white" />
          <span>Generating PDF...</span>
        </>
      ) : (
        <>
          <Download className="w-4 h-4 text-emerald-200" />
          <span>Download PDF Report</span>
        </>
      )}
    </button>
  );
}
