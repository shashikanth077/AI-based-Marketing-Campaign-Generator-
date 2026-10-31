export default function Options({ options, onChange, demo }) {
  const set = (patch) => onChange({ ...options, ...patch });
  const agent = options.mode === "agent";
  return (
    <section className="panel">
      <h2>2 · Options</h2>

      <div className="field">
        <span className="label">Pipeline</span>
        <div className="segmented" role="radiogroup" aria-label="Pipeline">
          <button role="radio" aria-checked={!agent} className={!agent ? "on" : ""} onClick={() => set({ mode: "direct", })}>
            Direct
          </button>
          <button role="radio" aria-checked={agent} className={agent ? "on" : ""} onClick={() => set({ mode: "agent", variants: 1 })}>
            Agents
          </button>
        </div>
        <p className="hint">
          {agent
            ? "Two ReAct agents: SQL agent fetches the product, campaign agent calls the generator tool. Slower; shows reasoning steps."
            : "One parameterised SQL lookup + one structured LLM call. Fast and deterministic."}
        </p>
      </div>

      <label className="check">
        <input type="checkbox" checked={options.creative} onChange={(e) => set({ creative: e.target.checked })} />
        <span>Creative writing</span>
      </label>
      <div className={`field ${options.creative ? "" : "disabled"}`}>
        <label className="label" htmlFor="temp">
          Temperature <b>{options.temperature.toFixed(1)}</b>
        </label>
        <input
          id="temp" type="range" min="0" max="2" step="0.1" value={options.temperature}
          disabled={!options.creative}
          onChange={(e) => set({ temperature: parseFloat(e.target.value) })}
        />
        <p className="hint">0 = deterministic · ~1 = creative · 2 = often incoherent. Facts and SQL always use 0.</p>
      </div>

      <div className={`field ${agent ? "disabled" : ""}`}>
        <label className="label" htmlFor="variants">A/B variants</label>
        <select id="variants" value={options.variants} disabled={agent} onChange={(e) => set({ variants: Number(e.target.value) })}>
          <option value={1}>1 (single draft)</option>
          <option value={2}>2 variants</option>
          <option value={3}>3 variants</option>
        </select>
      </div>

      <label className="check">
        <input type="checkbox" checked={options.safety_check} onChange={(e) => set({ safety_check: e.target.checked })} />
        <span>Llama Guard safety check{demo ? " (needs API key)" : ""}</span>
      </label>
    </section>
  );
}
