export const API_BASE = 'http://localhost:5000/api';

export async function apiReset(options = {}) {
  const res = await fetch(`${API_BASE}/reset`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(options)
  });
  const data = await res.json();
  if (!data.ok) throw new Error('reset failed');
  return data.state;
}

export async function apiStep(steps = 1) {
  const res = await fetch(`${API_BASE}/step`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ steps })
  });
  const data = await res.json();
  if (!data.ok) throw new Error('step failed');
  return data.state;
}

export async function apiLayouts() {
  const res = await fetch(`${API_BASE}/layouts`);
  const data = await res.json();
  if (!data.ok) throw new Error('layouts failed');
  return data.layouts;
}

export async function apiMeta() {
  const res = await fetch(`${API_BASE}/meta`);
  const data = await res.json();
  if (!data.ok) throw new Error('meta failed');
  return data;
}

export async function apiModels() {
  const res = await fetch(`${API_BASE}/models`);
  const data = await res.json();
  if (!data.ok) throw new Error('models failed');
  return data;
}

export async function apiTrain(options = {}) {
  const res = await fetch(`${API_BASE}/train`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(options)
  });
  const data = await res.json();
  if (!data.ok) throw new Error('train failed');
  return data;
}
