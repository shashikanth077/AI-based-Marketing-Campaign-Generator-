export default function History({ items, onOpen, onClear }) {
  if (!items.length) return null;
  return (
    <section className="panel">
      <div className="panel-head">
        <h2>Recent</h2>
        <button className="link" onClick={onClear}>Clear</button>
      </div>
      <ul className="history">
        {items.map((it) => (
          <li key={it.id}>
            <button onClick={() => onOpen(it)}>
              <span>{it.data.product.product_name}</span>
              <span className="muted">
                {it.data.mode} · {new Date(it.at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
              </span>
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}
