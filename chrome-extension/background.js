chrome.action.onClicked.addListener((tab) => {
  if (tab && tab.url) {
    const targetUrl = encodeURIComponent(tab.url);
    const auditAppUrl = `http://localhost:5173/?url=${targetUrl}`;
    chrome.tabs.create({ url: auditAppUrl });
  }
});
