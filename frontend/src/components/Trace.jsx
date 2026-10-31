export default function Trace({ steps, demo }) {
  if (!steps.length) return null;
  return (
    <details className="card trace">
      <summary>
        Agent reasoning trace <span className="muted">({steps.length} tool call{steps.length > 1 ? "s" : ""}{demo ? ", illustrative" : ""})</span>
      </summary>
      <ol>
        {steps.map((s, i) => (
          <li key={i}>
            <div className="step-head">
              <span className={`pill ${s.agent === "SQL agent" ? "blue" : "violet"}`}>{s.agent}</span>
              <code>{s.tool}</code>
            </div>
            {s.thought && <p className="thought"><b>Thought:</b> {s.thought}</p>}
            {s.input && <pre><b>Input</b>{"\n"}{s.input}</pre>}
            <pre><b>Observation</b>{"\n"}{s.observation}</pre>
          </li>
        ))}
      </ol>
    </details>
  );
}
