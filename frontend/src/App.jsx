import { useCallback, useEffect, useRef, useState } from "react";
import { createCampaign, getHealth, getProducts } from "./api.js";
import { load, save } from "./storage.js";
import Header from "./components/Header.jsx";
import ProductPicker from "./components/ProductPicker.jsx";
import Options from "./components/Options.jsx";
import Result from "./components/Result.jsx";
import History from "./components/History.jsx";

const DEFAULT_OPTIONS = { mode: "direct", creative: false, temperature: 1.0, safety_check: false, variants: 1 };

export default function App() {
  const [health, setHealth] = useState(null);
  const [products, setProducts] = useState([]);
  const [loadError, setLoadError] = useState("");
  const [selected, setSelected] = useState(load("cg-selected", "P1011"));
  const [options, setOptions] = useState({ ...DEFAULT_OPTIONS, ...load("cg-options", {}) });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [history, setHistory] = useState(load("cg-history", []));
  const abortRef = useRef(null);

  useEffect(() => {
    Promise.all([getHealth(), getProducts()])
      .then(([h, p]) => {
        setHealth(h);
        setProducts(p);
      })
      .catch((e) => setLoadError(e.message));
  }, []);

  useEffect(() => save("cg-selected", selected), [selected]);
  useEffect(() => save("cg-options", options), [options]);

  const generate = useCallback(async () => {
    const controller = new AbortController();
    abortRef.current = controller;
    setLoading(true);
    setError("");
    try {
      const data = await createCampaign({ product_id: selected, ...options }, controller.signal);
      setResult(data);
      setHistory((prev) => {
        const next = [{ id: Date.now(), at: new Date().toISOString(), data }, ...prev].slice(0, 8);
        save("cg-history", next);
        return next;
      });
    } catch (e) {
      if (e.name !== "AbortError") setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [selected, options]);

  const cancel = () => abortRef.current?.abort();
  const product = products.find((p) => p.product_id === selected);

  return (
    <>
      <Header health={health} />
      <main className="layout">
        <aside className="sidebar">
          {loadError && (
            <div className="banner error" role="alert">
              Cannot reach the backend: {loadError}. Start it with <code>make start</code> or{" "}
              <code>uvicorn marketing_campaign.api:app</code>.
            </div>
          )}
          <ProductPicker products={products} selected={selected} onSelect={setSelected} />
          <Options options={options} onChange={setOptions} demo={health?.demo} />
          <div className="actions">
            {loading ? (
              <button className="btn" onClick={cancel}>Cancel</button>
            ) : (
              <button className="btn primary" onClick={generate} disabled={!product}>
                Generate campaign
              </button>
            )}
          </div>
          <History
            items={history}
            onOpen={(item) => {
              setResult(item.data);
              setSelected(item.data.product.product_id);
              setError("");
            }}
            onClear={() => {
              setHistory([]);
              save("cg-history", []);
            }}
          />
        </aside>
        <section className="content" aria-live="polite">
          <Result result={result} loading={loading} error={error} mode={options.mode} product={product} />
        </section>
      </main>
    </>
  );
}
