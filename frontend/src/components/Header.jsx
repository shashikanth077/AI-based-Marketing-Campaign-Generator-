import { useEffect, useState } from "react";
import { load, save } from "../storage.js";

export default function Header({ health }) {
  const [theme, setTheme] = useState(load("cg-theme", null));

  useEffect(() => {
    if (theme) document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);

  const toggle = () => {
    const dark = theme
      ? theme === "dark"
      : window.matchMedia("(prefers-color-scheme: dark)").matches;
    const next = dark ? "light" : "dark";
    setTheme(next);
    save("cg-theme", next);
  };

  return (
    <header className="topbar">
      <div className="brand">
        <span className="logo" aria-hidden="true">✦</span>
        <div>
          <h1>Campaign Generator</h1>
          <p>Product ID → SQL agent → Title, Email &amp; CTA</p>
        </div>
      </div>
      <div className="topbar-right">
        {health && (
          <span className={`pill ${health.demo ? "warn" : "good"}`} title={health.model || "No GROQ_API_KEY set"}>
            {health.demo ? "Demo mode (no LLM)" : `Live · ${health.model.split("/").pop()}`}
          </span>
        )}
        <button className="btn icon" onClick={toggle} aria-label="Toggle light/dark theme">◐</button>
      </div>
    </header>
  );
}
