const BACKEND_URL = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '');
const API_BASE = `${BACKEND_URL}/api/v1`;


/**
 * Ingest artifact (File upload, URL, or Text) for fraud analysis.
 */
export async function ingestArtifact({ file, url, textContent, inputTypeHint }) {
  if (file) {
    const formData = new FormData();
    formData.append('file', file);
    if (inputTypeHint) formData.append('input_type_hint', inputTypeHint);
    
    const res = await fetch(`${API_BASE}/ingest`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to ingest file');
    }
    return res.json();
  }

  const formData = new FormData();
  if (url) formData.append('url', url);
  if (textContent) formData.append('text_content', textContent);
  if (inputTypeHint) formData.append('input_type_hint', inputTypeHint);

  const res = await fetch(`${API_BASE}/ingest`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Failed to ingest data');
  }
  return res.json();
}

/**
 * Fetch case details by case ID.
 */
export async function getCaseDetails(caseId) {
  const res = await fetch(`${API_BASE}/cases/${caseId}`);
  if (!res.ok) {
    throw new Error(`Failed to fetch case ${caseId}`);
  }
  return res.json();
}

/**
 * Fetch list of recent cases.
 */
export async function listCases(status, limit = 20) {
  const params = new URLSearchParams();
  if (status) params.append('status', status);
  params.append('limit', limit.toString());

  const res = await fetch(`${API_BASE}/cases?${params.toString()}`);
  if (!res.ok) throw new Error('Failed to list cases');
  return res.json();
}

/**
 * Fetch aggregated threat intelligence.
 */
export async function getThreatIntel(days = 30) {
  const res = await fetch(`${API_BASE}/dashboard/threat-intel?days=${days}`);
  if (!res.ok) throw new Error('Failed to fetch threat intelligence');
  return res.json();
}

/**
 * Fetch fraud heatmap data.
 */
export async function getHeatmapData(days = 30) {
  const res = await fetch(`${API_BASE}/dashboard/heatmap?days=${days}`);
  if (!res.ok) throw new Error('Failed to fetch heatmap data');
  return res.json();
}

/**
 * Fetch emerging scam trends.
 */
export async function getScamTrends(days = 30) {
  const res = await fetch(`${API_BASE}/dashboard/trends?days=${days}`);
  if (!res.ok) throw new Error('Failed to fetch scam trends');
  return res.json();
}

/**
 * Fetch browser protection alerts.
 */
export async function getAlerts(severity, hours = 24) {
  const params = new URLSearchParams({ hours: hours.toString() });
  if (severity) params.append('severity', severity);

  const res = await fetch(`${API_BASE}/dashboard/alerts?${params.toString()}`);
  if (!res.ok) throw new Error('Failed to fetch alerts');
  return res.json();
}

/**
 * Generate a complaint draft for a case.
 */
export async function generateComplaint(caseId) {
  const res = await fetch(`${API_BASE}/complaints/${caseId}/generate`, {
    method: 'POST',
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Failed to generate complaint draft');
  }
  return res.json();
}

/**
 * Edit a complaint draft.
 */
export async function editComplaint(caseId, edits) {
  const res = await fetch(`${API_BASE}/complaints/${caseId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(edits),
  });
  if (!res.ok) throw new Error('Failed to edit complaint');
  return res.json();
}

/**
 * Confirm a complaint draft and render PDF.
 */
export async function confirmComplaint(caseId) {
  const res = await fetch(`${API_BASE}/complaints/${caseId}/confirm`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Failed to confirm complaint');
  return res.json();
}

/**
 * Get PDF download URL for a complaint.
 */
export function getComplaintPdfUrl(caseId) {
  return `${API_BASE}/complaints/${caseId}/pdf`;
}
