chrome.action.onClicked.addListener((tab) => {
  if (tab && tab.url) {
    const targetUrl = encodeURIComponent(tab.url);
    const auditAppUrl = `https://seo-agent-inky-seven.vercel.app/?url=${targetUrl}`;
    chrome.tabs.create({ url: auditAppUrl });
  }
});
