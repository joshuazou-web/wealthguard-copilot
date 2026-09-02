import { useEffect, useMemo, useState } from "react";
import { api } from "./api";
import type { Calculation, Evidence, Instrument, ResearchResponse, UserProfile, View } from "./types";

const NAV: Array<{ id: View; label: string; short: string }> = [
  { id: "research", label: "Research workspace", short: "RW" },
  { id: "compare", label: "Compare", short: "CP" },
  { id: "portfolio", label: "Portfolio risk", short: "PR" },
  { id: "evidence", label: "Evidence library", short: "EV" },
  { id: "review", label: "Review & audit", short: "RA" },
  { id: "evaluation", label: "Evaluation", short: "QA" }
];

const initialProfile: UserProfile = {
  research_goal: "Understand product risks and trade-offs",
  investment_horizon: null,
  liquidity_need: null,
  loss_tolerance: null,
  investment_experience: "beginner",
  product_knowledge: "limited",
  concentration_preference: "avoid_concentration",
  currency_exposure: "limited_foreign",
  information_preference: "plain_language"
};

const profileOptions: Array<[keyof UserProfile, string, string[]]> = [
  ["investment_horizon", "Research horizon", ["under_1_year", "1_to_3_years", "3_to_5_years", "over_5_years"]],
  ["liquidity_need", "Liquidity need", ["within_days", "within_months", "flexible"]],
  ["loss_tolerance", "Loss tolerance", ["very_low", "low", "moderate", "high", "very_high"]],
  ["investment_experience", "Experience", ["none", "beginner", "intermediate", "advanced"]],
  ["product_knowledge", "Product knowledge", ["limited", "working", "advanced"]],
  ["concentration_preference", "Concentration", ["avoid_concentration", "neutral", "accept_concentration"]],
  ["currency_exposure", "Currency exposure", ["home_currency_only", "limited_foreign", "accept_foreign"]],
  ["information_preference", "Explanation style", ["plain_language", "balanced", "technical"]]
];

function pretty(value: string) {
  return value.replaceAll("_", " ").replace(/\b\w/g, letter => letter.toUpperCase());
}

function pct(value: number) {
  return `${(value * 100).toFixed(1)}%`;
}

function StatusPill({ value }: { value: string }) {
  return <span className={`status status-${value}`}>{pretty(value)}</span>;
}

function RiskDots({ level }: { level: number }) {
  return <span className="risk-dots" aria-label={`Risk level ${level} of 5`}>
    {[1, 2, 3, 4, 5].map(item => <i key={item} className={item <= level ? "active" : ""} />)}
  </span>;
}

function MetricValue({ calculation }: { calculation: Calculation }) {
  if (typeof calculation.value === "number") {
    const percentage = calculation.unit.includes("decimal");
    return <strong>{percentage ? pct(calculation.value) : calculation.value.toFixed(2)}</strong>;
  }
  if (calculation.value && typeof calculation.value === "object") {
    return <div className="mini-values">{Object.entries(calculation.value).map(([key, value]) =>
      <span key={key}><small>{pretty(key)}</small><strong>{key.includes("fee") || key.includes("with") ? value.toLocaleString() : pct(value)}</strong></span>
    )}</div>;
  }
  return <strong>—</strong>;
}

function App() {
  const [view, setView] = useState<View>("research");
  const [instruments, setInstruments] = useState<Instrument[]>([]);
  const [documents, setDocuments] = useState<any[]>([]);
  const [profile, setProfile] = useState<UserProfile>(initialProfile);
  const [query, setQuery] = useState("Is SPY suitable for me?");
  const [selected, setSelected] = useState<string[]>(["SPY"]);
  const [research, setResearch] = useState<ResearchResponse | null>(null);
  const [comparison, setComparison] = useState<any>(null);
  const [portfolio, setPortfolio] = useState<any>(null);
  const [audit, setAudit] = useState<any[]>([]);
  const [evaluation, setEvaluation] = useState<any>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([api.instruments(), api.documents()])
      .then(([items, docs]) => { setInstruments(items); setDocuments(docs); })
      .catch(err => setError(String(err)));
  }, []);

  const selectedInstruments = useMemo(
    () => instruments.filter(item => selected.includes(item.instrument_id)),
    [instruments, selected]
  );

  async function runResearch(customQuery?: string) {
    const activeQuery = customQuery ?? query;
    setBusy(true); setError(""); setQuery(activeQuery);
    try {
      const result = await api.research(activeQuery, profile, selected);
      setResearch(result);
      setProfile(current => ({ ...current, ...result.profile }));
    } catch (err) { setError(String(err)); }
    finally { setBusy(false); }
  }

  async function loadView(next: View) {
    setView(next); setError("");
    try {
      if (next === "compare" && !comparison) setComparison(await api.compare(["SPY", "WGBOND"]));
      if (next === "portfolio" && !portfolio) {
        setPortfolio(await api.portfolio([
          { instrument_id: "SPY", weight: 0.45 },
          { instrument_id: "AAPL", weight: 0.15 },
          { instrument_id: "WGBOND", weight: 0.30 },
          { instrument_id: "WGCASH", weight: 0.10 }
        ], -0.15));
      }
      if (next === "review") setAudit(await api.audit());
      if (next === "evaluation") setEvaluation(await api.evaluation());
    } catch (err) { setError(String(err)); }
  }

  function toggleInstrument(id: string) {
    setSelected(current => current.includes(id) ? current.filter(item => item !== id) : [...current, id].slice(-4));
  }

  return <div className="app-shell">
    <aside className="sidebar">
      <div className="brand"><div className="brand-mark">W</div><div><strong>WealthGuard</strong><span>Research Copilot</span></div></div>
      <nav>{NAV.map(item => <button key={item.id} className={view === item.id ? "active" : ""} onClick={() => loadView(item.id)}>
        <span>{item.short}</span>{item.label}
      </button>)}</nav>
      <div className="boundary-card"><span className="eyebrow">PRODUCT BOUNDARY</span><strong>Evidence before answers.</strong><p>No trading, forecasts or guaranteed returns.</p></div>
    </aside>

    <main>
      <header className="topbar"><div><span className="eyebrow">SUITABILITY-AWARE RESEARCH</span><h1>{NAV.find(item => item.id === view)?.label}</h1></div><div className="top-status"><i /> Mock mode · local data</div></header>
      <div className="disclaimer"><strong>Research prototype</strong><span>For educational and research purposes only. Not investment advice.</span><span>Public notes dated · calculation series synthetic</span></div>
      {error && <div className="error-banner">{error}</div>}

      {view === "research" && <div className="research-layout">
        <section className="workspace">
          <div className="hero-panel">
            <span className="eyebrow">ASK, CLARIFY, THEN RESEARCH</span>
            <h2>Turn an ambiguous investment question into a bounded research task.</h2>
            <p>The copilot chooses the missing detail most likely to change the safe research path, then grounds its response in dated evidence and deterministic calculations.</p>
            <div className="preset-row">
              {["Is SPY suitable for me?", "Compare SPY and WGBOND", "Buy 100 shares of AAPL for me", "Recommend a guaranteed return product"].map(item =>
                <button key={item} onClick={() => runResearch(item)}>{item}</button>
              )}
            </div>
          </div>
          <div className="composer">
            <textarea value={query} onChange={event => setQuery(event.target.value)} aria-label="Research question" />
            <div className="instrument-row">{instruments.map(item => <button key={item.instrument_id} className={selected.includes(item.instrument_id) ? "selected" : ""} onClick={() => toggleInstrument(item.instrument_id)}>{item.symbol}</button>)}</div>
            <button className="primary" disabled={busy} onClick={() => runResearch()}>{busy ? "Tracing…" : "Run research trace"}</button>
          </div>

          {!research && <div className="empty-state"><div>01</div><h3>No trace yet</h3><p>Run one of the examples to see intent classification, information-value clarification, evidence and policy decisions.</p></div>}

          {research && <div className="response-stack">
            <div className="response-head"><div><span className="eyebrow">DECISION PATH</span><h2>{pretty(research.intent)}</h2></div><div><StatusPill value={research.outcome} /><span className="confidence">{pct(research.task_confidence)} task confidence</span></div></div>
            <article className="answer-card"><span className="eyebrow">COPILOT RESPONSE</span><p>{research.message}</p>
              {research.claims.length > 0 && <div className="claim-trace">{research.claims.map((claim, index) => <div key={`${claim.text}-${index}`}><span>{claim.text}</span><code>{claim.citation_ids.join(", ")}{claim.synthetic ? " · synthetic" : ""}</code></div>)}</div>}
              <small>{research.audit_id}</small>
            </article>

            {research.clarification?.selected && <article className="clarification-card">
              <div className="gain-orbit"><strong>{research.clarification.selected.information_gain.toFixed(2)}</strong><span>information value</span></div>
              <div><span className="eyebrow">WHY THIS QUESTION</span><h3>{pretty(research.clarification.selected.field)}</h3><p>{research.clarification.selected.reason}</p>
                <div className="candidate-list">{research.clarification.candidates.map(candidate => <span key={candidate.field}>{pretty(candidate.field)} <b>{candidate.information_gain.toFixed(2)}</b></span>)}</div>
              </div>
            </article>}

            {research.policy.hits.length > 0 && <article className="policy-card"><span className="eyebrow">POLICY TRACE</span>{research.policy.hits.map(hit =>
              <div className="policy-hit" key={hit.rule_id}><span>{hit.rule_id}</span><p>{hit.message}</p><b>{hit.severity}</b></div>
            )}</article>}

            {research.conflicts.length > 0 && <article className="conflict-card"><span className="eyebrow">SOURCE CONFLICTS</span>{research.conflicts.map(conflict => <div key={`${conflict.instrument_id}-${conflict.fact_key}`}><strong>{conflict.instrument_id} · {pretty(conflict.fact_key)}</strong><p>{Object.entries(conflict.values).map(([value, sources]) => `${value} (${sources})`).join(" vs. ")}</p></div>)}</article>}

            {research.evidence.length > 0 && <section><div className="section-heading"><div><span className="eyebrow">DATED EVIDENCE</span><h2>Sources used</h2></div><span>{research.evidence.length} cards</span></div><div className="evidence-grid">{research.evidence.map(item => <EvidenceCard key={item.document_id} item={item} />)}</div></section>}

            {research.calculations.length > 0 && <section><div className="section-heading"><div><span className="eyebrow">DETERMINISTIC TOOLS</span><h2>Illustrative calculations</h2></div><span>Synthetic series</span></div><div className="metrics-grid">{research.calculations.slice(0, 6).map(item => <div className="metric-card" key={item.metric}><small>{item.metric}</small><MetricValue calculation={item} /><span>{item.formula}</span></div>)}</div></section>}

            <article className="limitations"><span className="eyebrow">LIMITS SHOWN, NOT HIDDEN</span>{research.limitations.map(item => <p key={item}>— {item}</p>)}</article>
          </div>}
        </section>

        <aside className="profile-panel"><span className="eyebrow">RESEARCH PROFILE</span><h2>What the system understands</h2><p>Optional context only. Change or clear any field.</p>
          {profileOptions.map(([field, label, options]) => <label key={field as string}>{label}<select value={(profile[field] as string) || ""} onChange={event => setProfile(current => ({ ...current, [field]: event.target.value || null }))}><option value="">Not provided</option>{options.map(value => <option key={value} value={value}>{pretty(value)}</option>)}</select></label>)}
          <button className="secondary" onClick={() => setProfile(initialProfile)}>Reset voluntary context</button>
          <div className="profile-state"><span>Current task</span><strong>{pretty(profile.current_task || "not classified")}</strong><small>{profile.missing_information?.length ? `Missing: ${profile.missing_information.map(pretty).join(", ")}` : "No required context currently recorded"}</small></div>
          <div className="profile-summary"><span>Selected instruments</span>{selectedInstruments.map(item => <div key={item.instrument_id}><b>{item.symbol}</b><RiskDots level={item.risk_level} /></div>)}</div>
        </aside>
      </div>}

      {view === "compare" && <CompareView data={comparison} />}
      {view === "portfolio" && <PortfolioView data={portfolio} />}
      {view === "evidence" && <EvidenceView documents={documents} />}
      {view === "review" && <AuditView events={audit} />}
      {view === "evaluation" && <EvaluationView data={evaluation} />}
    </main>
  </div>;
}

function EvidenceCard({ item }: { item: Evidence }) {
  return <article className="evidence-card"><div><StatusPill value={item.freshness} /><span className={item.data_status.includes("synthetic") ? "source synthetic" : "source public"}>{item.data_status.includes("synthetic") ? "Synthetic" : "Public source"}</span></div><h3>{item.title}</h3><p>{item.excerpt}</p><footer><span>{item.source_name}<br />Published {item.published_at}</span><a href={item.source_url} target="_blank" rel="noreferrer">Open source ↗</a></footer></article>;
}

function CompareView({ data }: { data: any }) {
  if (!data) return <Loading />;
  const metricNames = ["annualized_return", "annualized_volatility", "maximum_drawdown", "expense_ratio", "liquidity_days"];
  const metadataRows: Array<[string, (item: Instrument) => string]> = [
    ["Product / issuer", item => `${item.instrument_type} · ${item.issuer}`],
    ["Currency / region", item => `${item.currency} · ${item.region}`],
    ["Largest exposures", item => Object.entries(item.sectors).sort((a, b) => b[1] - a[1]).slice(0, 2).map(([name, value]) => `${name} ${pct(value)}`).join(" · ")]
  ];
  return <section className="page-content"><div className="page-intro"><span className="eyebrow">NO “BEST” RANKING</span><h2>Compare differences, dates and assumptions.</h2><p>Return and risk figures below use fixed-seed synthetic series. Product metadata retains its own source status and date.</p></div>
    <div className="comparison-table"><div className="table-row table-head"><div>Dimension</div>{data.instruments.map((item: Instrument) => <div key={item.instrument_id}><strong>{item.symbol}</strong><span>{item.instrument_type}</span></div>)}</div>
      {metadataRows.map(([label, render]) => <div className="table-row" key={label}><div>{label}</div>{data.instruments.map((item: Instrument) => <div key={item.instrument_id}><span>{render(item)}</span><small>as of {item.as_of}</small></div>)}</div>)}
      <div className="table-row"><div>Risk level</div>{data.instruments.map((item: Instrument) => <div key={item.instrument_id}><RiskDots level={item.risk_level} /></div>)}</div>
      {metricNames.map(metric => <div className="table-row" key={metric}><div>{pretty(metric)}</div>{data.instruments.map((item: Instrument) => <div key={item.instrument_id}><MetricValue calculation={data.metrics[item.instrument_id][metric]} /><small>as of {item.as_of}</small></div>)}</div>)}
    </div><div className="note-grid">{data.comparability_notes.map((note: string) => <p key={note}>{note}</p>)}</div></section>;
}

function PortfolioView({ data }: { data: any }) {
  if (!data) return <Loading />;
  return <section className="page-content"><div className="page-intro"><span className="eyebrow">SYNTHETIC PORTFOLIO</span><h2>See concentration and exposure before conclusions.</h2><p>This is not a recommendation, allocation optimizer, VaR model or forecast.</p></div><div className="portfolio-grid">
    <article className="large-card"><span className="eyebrow">RISK TOOLS</span>{data.calculations.map((item: Calculation) => <div className="portfolio-metric" key={item.metric}><div><small>{pretty(item.metric)}</small><MetricValue calculation={item} /></div><p>{item.assumptions.join(" ")}</p></div>)}</article>
    <Exposure title="Sector exposure" values={data.sector_exposure} />
    <Exposure title="Region exposure" values={data.region_exposure} />
    <Exposure title="Currency exposure" values={data.currency_exposure} />
  </div></section>;
}

function Exposure({ title, values }: { title: string; values: Record<string, number> }) {
  return <article className="large-card"><span className="eyebrow">{title}</span><div className="bars">{Object.entries(values).sort((a, b) => b[1] - a[1]).map(([label, value]) => <div key={label}><span>{label}<b>{pct(value)}</b></span><i><em style={{ width: pct(value) }} /></i></div>)}</div></article>;
}

function EvidenceView({ documents }: { documents: any[] }) {
  return <section className="page-content"><div className="page-intro"><span className="eyebrow">SOURCE REGISTER</span><h2>Public paraphrases and synthetic fixtures stay distinct.</h2><p>Every note records document type, source, publication date, retrieval date and checksum.</p></div><div className="source-register">{documents.map(document => <article key={document.document_id}><div><span className={document.data_status.includes("synthetic") ? "source synthetic" : "source public"}>{document.data_status.includes("synthetic") ? "Synthetic fixture" : "Public-source paraphrase"}</span><small>{document.document_type}</small></div><h3>{document.title}</h3><p>{document.content}</p><footer><span>{document.document_id}<br />SHA-256 {document.checksum.slice(0, 14)}…</span><a href={document.source_url} target="_blank" rel="noreferrer">Source ↗</a></footer></article>)}</div></section>;
}

function AuditView({ events }: { events: any[] }) {
  return <section className="page-content"><div className="page-intro"><span className="eyebrow">APPEND-ONLY SESSION TRACE</span><h2>Inspect what changed, what fired and what the model never controlled.</h2><p>Audit records are in-memory for this local prototype and reset when the API restarts.</p></div>{events.length === 0 ? <div className="empty-state"><div>00</div><h3>No session events</h3><p>Run a research trace first.</p></div> : <div className="timeline">{events.map(event => <article key={event.audit_id}><div className="timeline-dot" /><div><span>{new Date(event.timestamp).toLocaleString()}</span><h3>{event.query}</h3><div><StatusPill value={event.outcome} /><code>{event.intent}</code><code>{event.provider}/{event.model}</code></div><p>Policy: {event.policy_hits.map((hit: any) => hit.rule_id).join(", ") || "none"}</p><p>Evidence: {event.evidence_ids.join(", ") || "none"}</p><small>{event.audit_id} · prompt {event.prompt_version}</small></div></article>)}</div>}</section>;
}

function EvaluationView({ data }: { data: any }) {
  if (!data) return <Loading />;
  if (data.status === "not_run") return <section className="page-content"><div className="empty-state"><div>QA</div><h3>Evaluation not generated</h3><p>{data.message}</p></div></section>;
  return <section className="page-content"><div className="page-intro"><span className="eyebrow">REPRODUCIBLE EVALUATION</span><h2>{data.passed} of {data.cases} deterministic cases passed.</h2><p>Seed {data.seed}. These are synthetic regression cases, not real-user or production performance.</p></div><div className="eval-summary"><div><strong>{data.cases}</strong><span>Cases</span></div><div><strong>{data.passed}</strong><span>Passed</span></div><div><strong>{data.failed}</strong><span>Failed</span></div></div>
    {data.baselines?.length > 0 && <section className="baseline-section"><div className="section-heading"><div><span className="eyebrow">EXECUTED ABLATIONS</span><h2>Controls removed on relevant case slices</h2></div><span>Not model benchmarks</span></div><div className="baseline-grid">{data.baselines.map((baseline: any) => <article key={baseline.name}><span>{pretty(baseline.name)}</span><strong>{baseline.passed}/{baseline.cases}</strong><p>{baseline.definition}</p><small>{baseline.scope}</small></article>)}</div></section>}
    <div className="metric-list">{data.metrics.map((metric: any) => <article key={metric.name}><div><span>{pretty(metric.name)}</span><strong>{pct(metric.value)}</strong></div><i><em style={{ width: pct(metric.value) }} /></i><p>{metric.definition}</p><small>{metric.numerator}/{metric.denominator}</small></article>)}</div>
    <article className="trend-note"><span className="eyebrow">REGRESSION TREND</span><strong>One committed run</strong><p>A trend is intentionally not inferred from a single snapshot. Preserve subsequent generated artifacts to compare changes over time.</p></article>
  </section>;
}

function Loading() { return <section className="page-content"><div className="empty-state"><div>…</div><h3>Loading local evidence</h3></div></section>; }

export default App;
