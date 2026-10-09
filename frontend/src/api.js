const API_BASE = import.meta.env.PROD ? "/api" : (import.meta.env.VITE_API_URL || "http://localhost:5000/api");

// Generate a random session ID once when the app loads
const sessionId = Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);

// Helper to inject headers
function getHeaders(extraHeaders = {}) {
  return {
    "X-Session-ID": sessionId,
    ...extraHeaders
  };
}

export async function sendQuery(query) {
  const res = await fetch(`${API_BASE}/query`, {
    method: "POST",
    headers: getHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ query }),
  });
  return res.json();
}

export async function uploadCSV(file) {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_BASE}/upload`, {
    method: "POST",
    headers: getHeaders(), // FormData sets its own Content-Type, just need session ID
    body: formData,
  });
  return res.json();
}

export async function fetchSchema() {
  const res = await fetch(`${API_BASE}/schema`, { headers: getHeaders() });
  return res.json();
}

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/health`, { headers: getHeaders() });
  return res.json();
}

export async function fetchDatasets() {
  const res = await fetch(`${API_BASE}/datasets`, { headers: getHeaders() });
  return res.json();
}

export async function loadDataset(filename) {
  const res = await fetch(`${API_BASE}/datasets/load`, {
    method: "POST",
    headers: getHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify({ filename }),
  });
  return res.json();
}

