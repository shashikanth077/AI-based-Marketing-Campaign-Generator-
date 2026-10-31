import CopyButton from "./CopyButton.jsx";

export default function CampaignCard({ campaign, disclaimer }) {
  const all = `${campaign.title}\n\nSubject: ${campaign.email_subject}\n\n${campaign.email_body}\n\nCTA: ${campaign.cta}\n\n${disclaimer}`;
  const failed = campaign.checks.filter((c) => !c.passed).length;
  return (
    <div className="campaign">
      <div className="card hero">
        <div className="card-head"><span className="eyebrow">Marketing title</span><CopyButton text={campaign.title} /></div>
        <p className="title">{campaign.title}</p>
      </div>

      <div className="card">
        <div className="card-head"><span className="eyebrow">Email draft</span><CopyButton text={`Subject: ${campaign.email_subject}\n\n${campaign.email_body}`} /></div>
        <p className="subject"><span className="muted">Subject:</span> {campaign.email_subject}</p>
        <div className="email">{campaign.email_body}</div>
        <p className="disclaimer">{disclaimer}</p>
      </div>

      <div className="card cta-card">
        <div className="card-head"><span className="eyebrow">Call to action</span><CopyButton text={campaign.cta} /></div>
        <p className="cta">{campaign.cta}</p>
      </div>

      <div className="card">
        <div className="card-head">
          <span className="eyebrow">Quality &amp; compliance checks</span>
          <span className={`pill ${failed ? "warn" : "good"}`}>{failed ? `${failed} to review` : "All passed"}</span>
        </div>
        <ul className="checks">
          {campaign.checks.map((c) => (
            <li key={c.id} className={c.passed ? "ok" : "fail"}>
              <span className="mark" aria-hidden="true">{c.passed ? "✓" : "✕"}</span>
              <span>{c.label}</span>
              <span className="muted">{c.detail}</span>
            </li>
          ))}
        </ul>
      </div>

      <div className="toolbar"><CopyButton text={all} label="Copy full campaign" /></div>
    </div>
  );
}
