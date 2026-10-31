export default function ProductPicker({ products, selected, onSelect }) {
  return (
    <section className="panel">
      <h2>1 · Choose a product</h2>
      {products.length === 0 && <p className="muted">Loading products…</p>}
      <div className="product-list" role="radiogroup" aria-label="Products">
        {products.map((p) => {
          const active = p.product_id === selected;
          return (
            <button
              key={p.product_id}
              role="radio"
              aria-checked={active}
              className={`product ${active ? "active" : ""}`}
              onClick={() => onSelect(p.product_id)}
            >
              <span className="product-id">{p.product_id}</span>
              <span className="product-name">{p.product_name}</span>
              <span className="product-meta">
                Age {p.target_age} · {p.target_profession}
              </span>
            </button>
          );
        })}
      </div>
    </section>
  );
}
