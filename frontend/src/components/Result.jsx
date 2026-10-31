import { useState, useEffect } from "react";
import CampaignCard from "./CampaignCard.jsx";
import Trace from "./Trace.jsx";

function Empty({ product }) {
  return (
    <div className="empty">
      <div className="empty-icon" aria-hidden="true">✦</div>
      <h2>Ready when you are</h2>
      <p>
        {product ? <>Selected <b>{product.product_name}</b>.</> : "Pick a product."} Press <b>Generate campaign</b> to
        create a title, email draft and call-to-action tailored to its audience.
      </p>
      {product && (
        <div className="card product-card">
          <span className="eyebrow">Product details fetched from the database</span>
          <p>{product.product_details}</p>
          <p className="muted">Target: age {product.target_age} · {product.target_profession}</p>
        </div>
      )}
    </div>
  );
}

function Skeleton({ mode }) {
  return (
    <div className="loading" role="status">
      <div className="spinner" aria-hidden="true" />
      <p>{mode === "agent" ? "Agents are reasoning: querying the database, then writing the campaign…" : "Fetching product and writing the campaign…"}</p>
      <p className="muted">This can take 5–30 seconds on the free Groq tier.</p>
      <div className="skeleton" /><div className="skeleton tall" /><div className="skeleton" />
    </div>
  );
}

export default function Result({ result, loading, error, mode, product }) {
  const [tab, setTab] = useState(0);
  useEffect(() => setTab(0), [result]);

  if (loading) return <Skeleton mode={mode} />;
  return (
    <>
      {error && <div className="banner error" role="alert">{error}</div>}
      {!result ? (
        <Empty product={product} />
      ) : (
        <>
          <div className="meta">
            <h2>{result.product.product_name}</h2>
            <div className="meta-pills">
              <span className="pill">{result.mode === "agent" ? "Agents" : "Direct"}</span>
              <span className="pill">{(result.latency_ms / 1000).toFixed(1)}s</span>
              <span className={`pill ${result.demo ? "warn" : ""}`}>{result.model.split("/").pop()}</span>
              {result.safety.checked && (
                <span className={`pill ${result.safety.safe ? "good" : "bad"}`}>{result.safety.safe ? "Llama Guard: safe" : "Llama Guard: flagged"}</span>
              )}
            </div>
          </div>
          {result.warnings.map((w) => <div key={w} className="banner">{w}</div>)}
          {result.campaigns.length === 0 && <div className="banner error">All generated content was withheld by the safety check.</div>}
          {result.campaigns.length > 1 && (
            <div className="tabs" role="tablist">
              {result.campaigns.map((_, i) => (
                <button key={i} role="tab" aria-selected={tab === i} className={tab === i ? "on" : ""} onClick={() => setTab(i)}>
                  Variant {String.fromCharCode(65 + i)}
                </button>
              ))}
            </div>
          )}
          {result.campaigns[tab] && <CampaignCard campaign={result.campaigns[tab]} disclaimer={result.disclaimer} />}
          <Trace steps={result.steps} demo={result.demo} />
        </>
      )}
    </>
  );
}
