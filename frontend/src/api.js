// Thin fetch wrapper. FastAPI errors arrive as {detail: string | [{msg}]}.
async function request(path, options = {}) {
  const res = await fetch(path, { headers: { "Content-Type": "application/json" }, ...options });
  const body = await res.json().catch(() => null);
  if (!res.ok) {
    const d = body?.detail;
    const msg = Array.isArray(d) ? d.map((e) => e.msg).join("; ") : d;
    throw new Error(msg || `Request failed (${res.status})`);
  }
  return body;
}

export const getHealth = () => request("/api/health");
export const getProducts = () => request("/api/products");
export const createCampaign = (payload, signal) =>
  request("/api/campaigns", { method: "POST", body: JSON.stringify(payload), signal });
