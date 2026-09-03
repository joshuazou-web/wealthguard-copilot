import { useEffect, useMemo, useState } from "react";
import { api } from "./api";
import { displayValue, localizeText, pick } from "./i18n";
import type { Language } from "./i18n";
import { createDogfoodState, downloadDogfoodData, usePersistentState } from "./storage";
import type { DogfoodState } from "./storage";
import type { Calculation, Evidence, Instrument, ResearchResponse, UserProfile, View } from "./types";

const NAV: Array<{ id: View; en: string; zh: string; short: string }> = [
  { id: "research", en: "Evidence protection", zh: "证据保护", short: "EP" },
  { id: "compare", en: "Compare", zh: "产品比较", short: "CP" },
  { id: "portfolio", en: "Portfolio risk", zh: "组合风险", short: "PR" },
  { id: "evidence", en: "Evidence library", zh: "证据库", short: "EV" },
  { id: "review", en: "Review & audit", zh: "复核审计", short: "RA" },
  { id: "evaluation", en: "Evaluation", zh: "系统评测", short: "QA" }
];

const PRESETS = [
  { en: "Is SPY suitable for me?", zh: "SPY 适合我吗？" },
  { en: "Compare SPY and WGBOND", zh: "比较 SPY 与 WGBOND" },
  { en: "Buy 100 shares of AAPL for me", zh: "替我买入 100 股 AAPL" },
  { en: "Recommend a guaranteed return product", zh: "推荐一个稳赚产品" }
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

const profileOptions: Array<[keyof UserProfile, string, string, string[]]> = [
  ["investment_horizon", "Research horizon", "研究期限", ["under_1_year", "1_to_3_years", "3_to_5_years", "over_5_years"]],
  ["liquidity_need", "Liquidity need", "流动性需求", ["within_days", "within_months", "flexible"]],
  ["loss_tolerance", "Loss tolerance", "亏损容忍度", ["very_low", "low", "moderate", "high", "very_high"]],
  ["investment_experience", "Experience", "投资经验", ["none", "beginner", "intermediate", "advanced"]],
  ["product_knowledge", "Product knowledge", "产品知识", ["limited", "working", "advanced"]],
  ["concentration_preference", "Concentration", "集中度偏好", ["avoid_concentration", "neutral", "accept_concentration"]],
  ["currency_exposure", "Currency exposure", "币种敞口", ["home_currency_only", "limited_foreign", "accept_foreign"]],
  ["information_preference", "Explanation style", "说明方式", ["plain_language", "balanced", "technical"]]
];

function pretty(value: string, language: Language = "en") {
  return displayValue(value, language);
}

function pct(value: number) {
  return `${(value * 100).toFixed(1)}%`;
}

function StatusPill({ value, language = "en" }: { value: string; language?: Language }) {
  return <span className={`status status-${value}`}>{pretty(value, language)}</span>;
}

function RiskDots({ level, language = "en" }: { level: number; language?: Language }) {
  return <span className="risk-dots" aria-label={pick(language, `Risk level ${level} of 5`, `风险等级 ${level}/5`)}>
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
  const [profile, setProfile] = usePersistentState<UserProfile>("wg-profile-v1", initialProfile);
  const [query, setQuery] = usePersistentState("wg-query-v1", "Is SPY suitable for me?");
  const [selected, setSelected] = usePersistentState<string[]>("wg-selected-v1", ["SPY"]);
  const [dogfood, setDogfood] = usePersistentState<DogfoodState>("wg-dogfood-v1", createDogfoodState());
  const [sessionId] = usePersistentState("wg-session-v1", crypto.randomUUID());
  const [language, setLanguage] = usePersistentState<Language>("wg-language-v1", "en");
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

  useEffect(() => {
    const today = new Date().toISOString().slice(0, 10);
    setDogfood(current => current.visitDays.includes(today)
      ? current
      : { ...current, visitDays: [...current.visitDays, today] });
  }, [setDogfood]);

  useEffect(() => {
    document.documentElement.lang = language === "zh" ? "zh-CN" : "en";
  }, [language]);

  const selectedInstruments = useMemo(
    () => instruments.filter(item => selected.includes(item.instrument_id)),
    [instruments, selected]
  );

  async function runResearch(customQuery?: string) {
    const visibleQuery = customQuery ?? query;
    const canonicalQuery = PRESETS.find(item => item.en === visibleQuery || item.zh === visibleQuery)?.en ?? visibleQuery;
    setBusy(true); setError(""); setQuery(visibleQuery);
    try {
      const result = await api.research(sessionId, canonicalQuery, profile, selected);
      setResearch(result);
      setProfile(current => ({ ...current, ...result.profile }));
      setDogfood(current => ({
        ...current,
        sessions: [{
          id: result.audit_id,
          occurredAt: new Date().toISOString(),
          query: visibleQuery,
          outcome: result.outcome,
          evidenceCount: result.evidence.length,
          evidenceOpened: 0
        }, ...current.sessions].slice(0, 200)
      }));
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
      if (next === "review") setAudit(await api.audit(sessionId));
      if (next === "evaluation") setEvaluation(await api.evaluation());
    } catch (err) { setError(String(err)); }
  }

  function toggleInstrument(id: string) {
    setSelected(current => current.includes(id) ? current.filter(item => item !== id) : [...current, id].slice(-4));
  }

  function recordEvidenceOpen() {
    if (!research) return;
    setDogfood(current => ({
      ...current,
      sessions: current.sessions.map(session => session.id === research.audit_id
        ? { ...session, evidenceOpened: session.evidenceOpened + 1 }
        : session)
    }));
  }

  function recordFeedback(feedback: "useful" | "needs_work") {
    if (!research) return;
    setDogfood(current => ({
      ...current,
      sessions: current.sessions.map(session => session.id === research.audit_id
        ? { ...session, feedback }
        : session)
    }));
  }

  function recordMiniProgramSignal(reason: "faster_entry" | "notifications" | "wechat_sharing") {
    setDogfood(current => ({
      ...current,
      miniProgramSignals: [...current.miniProgramSignals, { occurredAt: new Date().toISOString(), reason }]
    }));
  }

  function toggleLanguage() {
    const next = language === "en" ? "zh" : "en";
    const preset = PRESETS.find(item => item.en === query || item.zh === query);
    if (preset) setQuery(preset[next]);
    setLanguage(next);
  }

  return <div className="app-shell">
    <aside className="sidebar">
      <div className="brand"><div className="brand-mark">W</div><div><strong>WealthGuard</strong><span>{pick(language, "Evidence protection", "证据化研究保护")}</span></div></div>
      <nav>{NAV.map(item => <button key={item.id} className={view === item.id ? "active" : ""} onClick={() => loadView(item.id)}>
        <span>{item.short}</span>{pick(language, item.en, item.zh)}
      </button>)}</nav>
      <div className="boundary-card"><span className="eyebrow">{pick(language, "PRODUCT BOUNDARY", "产品边界")}</span><strong>{pick(language, "Evidence before conclusions.", "先核验证据，再形成结论。")}</strong><p>{pick(language, "Research protection—not a trading companion, adviser or execution tool.", "这是研究保护系统，不是交易伴侣、投顾或执行工具。")}</p></div>
    </aside>

    <main>
      <header className="topbar"><div><span className="eyebrow">{pick(language, "EVIDENCE-GROUNDED RESEARCH PROTECTION", "基于证据的金融研究保护")}</span><h1>{NAV.find(item => item.id === view) ? pick(language, NAV.find(item => item.id === view)!.en, NAV.find(item => item.id === view)!.zh) : ""}</h1></div><div className="top-actions"><div className="top-status"><i /> {pick(language, "Privacy-first · device-saved study", "隐私优先 · 数据保存在本机")}</div><button className="language-toggle" onClick={toggleLanguage} aria-label={pick(language, "Switch to Chinese", "切换到英文")}>{language === "en" ? "中文" : "EN"}</button></div></header>
      <div className="disclaimer"><strong>{pick(language, "Research prototype", "研究原型")}</strong><span>{pick(language, "For educational and research purposes only. Not investment advice.", "仅用于教育与研究，不构成投资建议。")}</span><span>{pick(language, "Public notes dated · calculation series synthetic", "公开资料标注日期 · 计算序列为合成数据")}</span></div>
      {error && <div className="error-banner">{error}</div>}

      {view === "research" && <div className="research-layout">
        <section className="workspace">
          <DogfoodPanel language={language} data={dogfood} onExport={() => downloadDogfoodData(dogfood)} onSignal={recordMiniProgramSignal} />
          <div className="hero-panel">
            <span className="eyebrow">{pick(language, "QUESTION → EVIDENCE → BOUNDARY → TRACE", "问题 → 证据 → 边界 → 轨迹")}</span>
            <h2>{pick(language, "Protect a financial research decision with inspectable evidence.", "用可核验的证据保护每一次金融研究判断。")}</h2>
            <p>{pick(language, "WealthGuard identifies the missing detail most likely to change the safe research path, checks dated official material, and exposes uncertainty before a conclusion can feel more certain than its evidence.", "WealthGuard 识别最可能改变安全研究路径的缺失信息，核查带日期的官方资料，并在结论显得比证据更确定之前揭示不确定性。")}</p>
            <div className="preset-row">
              {PRESETS.map(item =>
                <button key={item.en} onClick={() => runResearch(item[language])}>{pick(language, item.en, item.zh)}</button>
              )}
            </div>
          </div>
          <div className="composer">
            <textarea value={query} onChange={event => setQuery(event.target.value)} aria-label={pick(language, "Research question", "研究问题")} placeholder={pick(language, "Ask a research question…", "输入需要核验的金融研究问题……")} />
            <div className="instrument-row">{instruments.map(item => <button key={item.instrument_id} className={selected.includes(item.instrument_id) ? "selected" : ""} onClick={() => toggleInstrument(item.instrument_id)}>{item.symbol}</button>)}</div>
            <button className="primary" disabled={busy} onClick={() => runResearch()}>{busy ? pick(language, "Tracing…", "正在追溯……") : pick(language, "Run research trace", "开始证据追溯")}</button>
          </div>

          {!research && <div className="empty-state"><div>01</div><h3>{pick(language, "No trace yet", "尚无研究轨迹")}</h3><p>{pick(language, "Run one of the examples to see intent classification, information-value clarification, evidence and policy decisions.", "运行一个示例，查看意图分类、信息价值澄清、证据和策略判断。")}</p></div>}

          {research && <div className="response-stack">
            <div className="response-head"><div><span className="eyebrow">{pick(language, "DECISION PATH", "决策路径")}</span><h2>{pretty(research.intent, language)}</h2></div><div><StatusPill value={research.outcome} language={language} /><span className="confidence">{pct(research.task_confidence)} {pick(language, "task confidence", "任务置信度")}</span></div></div>
            <article className="answer-card"><span className="eyebrow">{pick(language, "COPILOT RESPONSE", "系统回复")}</span><p>{localizeText(research.message, language)}</p>
              {research.claims.length > 0 && <div className="claim-trace">{research.claims.map((claim, index) => <div key={`${claim.text}-${index}`}><span>{claim.text}</span><code>{claim.citation_ids.map(citationId => { const cited = research.evidence.find(item => (item.chunk_id || item.document_id) === citationId); return cited ? <a key={citationId} href={cited.locator_url || cited.source_url} target="_blank" rel="noreferrer">{citationId}</a> : citationId; })}{claim.synthetic ? " · synthetic" : ""}</code></div>)}</div>}
              <small>{research.audit_id}</small>
              <div className="feedback-row"><span>{pick(language, "Did this trace protect your research?", "这次追溯是否真正保护了你的研究判断？")}</span><button onClick={() => recordFeedback("useful")}>{pick(language, "Useful", "有帮助")}</button><button onClick={() => recordFeedback("needs_work")}>{pick(language, "Needs work", "需要改进")}</button></div>
            </article>

            {research.clarification?.selected && <article className="clarification-card">
              <div className="gain-orbit"><strong>{research.clarification.selected.information_gain.toFixed(2)}</strong><span>{pick(language, "information value", "信息价值")}</span></div>
              <div><span className="eyebrow">{pick(language, "WHY THIS QUESTION", "为什么问这个问题")}</span><h3>{pretty(research.clarification.selected.field, language)}</h3><p>{localizeText(research.clarification.selected.reason, language)}</p>
                <div className="candidate-list">{research.clarification.candidates.map(candidate => <span key={candidate.field}>{pretty(candidate.field, language)} <b>{candidate.information_gain.toFixed(2)}</b></span>)}</div>
              </div>
            </article>}

            {research.policy.hits.length > 0 && <article className="policy-card"><span className="eyebrow">{pick(language, "POLICY TRACE", "策略轨迹")}</span>{research.policy.hits.map(hit =>
              <div className="policy-hit" key={hit.rule_id}><span>{hit.rule_id}</span><p>{localizeText(hit.message, language)}</p><b>{pretty(hit.severity, language)}</b></div>
            )}</article>}

            {research.conflicts.length > 0 && <article className="conflict-card"><span className="eyebrow">{pick(language, "SOURCE CONFLICTS", "来源冲突")}</span>{research.conflicts.map(conflict => <div key={`${conflict.instrument_id}-${conflict.fact_key}`}><strong>{conflict.instrument_id} · {pretty(conflict.fact_key, language)}</strong><p>{Object.entries(conflict.values).map(([value, sources]) => `${value} (${sources})`).join(pick(language, " vs. ", " 与 "))}</p></div>)}</article>}

            {research.evidence.length > 0 && <section><div className="section-heading"><div><span className="eyebrow">{pick(language, "DATED EVIDENCE", "带日期的证据")}</span><h2>{pick(language, "Sources used", "本次使用的来源")}</h2></div><span>{research.evidence.length} {pick(language, "cards", "张证据卡")}</span></div><div className="evidence-grid">{research.evidence.map(item => <EvidenceCard language={language} key={item.chunk_id || item.document_id} item={item} onOpen={recordEvidenceOpen} />)}</div></section>}

            {research.calculations.length > 0 && <section><div className="section-heading"><div><span className="eyebrow">{pick(language, "DETERMINISTIC TOOLS", "确定性计算工具")}</span><h2>{pick(language, "Illustrative calculations", "示例计算")}</h2></div><span>{pick(language, "Synthetic series", "合成序列")}</span></div><div className="metrics-grid">{research.calculations.slice(0, 6).map(item => <div className="metric-card" key={item.metric}><small>{pretty(item.metric, language)}</small><MetricValue calculation={item} /><span>{item.formula}</span></div>)}</div></section>}

            <article className="limitations"><span className="eyebrow">{pick(language, "LIMITS SHOWN, NOT HIDDEN", "明确展示能力边界")}</span>{research.limitations.map(item => <p key={item}>— {localizeText(item, language)}</p>)}</article>
          </div>}
        </section>

        <aside className="profile-panel"><span className="eyebrow">{pick(language, "RESEARCH PROFILE", "研究档案")}</span><h2>{pick(language, "What the system understands", "系统当前理解")}</h2><p>{pick(language, "Optional context only. Change or clear any field.", "仅为可选背景信息，可修改、跳过或清除。")}</p>
          {profileOptions.map(([field, labelEn, labelZh, options]) => <label key={field as string}>{pick(language, labelEn, labelZh)}<select value={(profile[field] as string) || ""} onChange={event => setProfile(current => ({ ...current, [field]: event.target.value || null }))}><option value="">{pick(language, "Not provided", "未提供")}</option>{options.map(value => <option key={value} value={value}>{pretty(value, language)}</option>)}</select></label>)}
          <button className="secondary" onClick={() => setProfile(initialProfile)}>{pick(language, "Reset voluntary context", "重置自愿提供的信息")}</button>
          <div className="profile-state"><span>{pick(language, "Current task", "当前任务")}</span><strong>{pretty(profile.current_task || "not_classified", language)}</strong><small>{profile.missing_information?.length ? `${pick(language, "Missing", "缺失信息")}：${profile.missing_information.map(item => pretty(item, language)).join(pick(language, ", ", "、"))}` : pick(language, "No required context currently recorded", "当前没有必须补充的信息")}</small></div>
          <div className="profile-summary"><span>{pick(language, "Selected instruments", "已选研究标的")}</span>{selectedInstruments.map(item => <div key={item.instrument_id}><b>{item.symbol}</b><RiskDots level={item.risk_level} language={language} /></div>)}</div>
        </aside>
      </div>}

      {view === "compare" && <CompareView data={comparison} language={language} />}
      {view === "portfolio" && <PortfolioView data={portfolio} language={language} />}
      {view === "evidence" && <EvidenceView documents={documents} language={language} />}
      {view === "review" && <AuditView events={audit} language={language} />}
      {view === "evaluation" && <EvaluationView data={evaluation} language={language} />}
    </main>
  </div>;
}

function DogfoodPanel({ language, data, onExport, onSignal }: { language: Language; data: DogfoodState; onExport: () => void; onSignal: (reason: "faster_entry" | "notifications" | "wechat_sharing") => void }) {
  const start = new Date(data.startedAt);
  const elapsed = Math.max(1, Math.floor((Date.now() - start.getTime()) / 86400000) + 1);
  const day = Math.min(14, elapsed);
  const evidenceOpens = data.sessions.reduce((sum, session) => sum + session.evidenceOpened, 0);
  const feedback = data.sessions.filter(session => session.feedback).length;
  return <section className="dogfood-panel">
    <div className="dogfood-title"><div><span className="eyebrow">{pick(language, "14-DAY REAL-USE STUDY", "14 天真实使用验证")}</span><h2>{pick(language, `Day ${day} of 14 · evidence protection log`, `第 ${day}/14 天 · 证据保护记录`)}</h2></div><button onClick={onExport}>{pick(language, "Export my data", "导出我的数据")}</button></div>
    <div className="dogfood-metrics"><div><strong>{data.visitDays.length}</strong><span>{pick(language, "active days", "活跃天数")}</span></div><div><strong>{data.sessions.length}</strong><span>{pick(language, "research traces", "研究轨迹")}</span></div><div><strong>{evidenceOpens}</strong><span>{pick(language, "evidence opens", "原文打开")}</span></div><div><strong>{feedback}</strong><span>{pick(language, "rated traces", "已评价轨迹")}</span></div></div>
    <div className="mini-signals"><span>{pick(language, "Would a mini program solve a real problem today?", "今天是否出现了只有小程序才能解决的问题？")}</span><button onClick={() => onSignal("faster_entry")}>{pick(language, "Faster entry", "更快入口")}</button><button onClick={() => onSignal("notifications")}>{pick(language, "Notifications", "消息提醒")}</button><button onClick={() => onSignal("wechat_sharing")}>{pick(language, "WeChat sharing", "微信分享")}</button><small>{data.miniProgramSignals.length} {pick(language, "needs recorded", "项需求记录")}</small></div>
    <p>{pick(language, "Stored only in this browser. Do not enter account numbers, holdings, identity documents, or other sensitive financial data.", "数据仅保存在当前浏览器。请勿输入账户号码、真实持仓、身份证件或其他敏感金融信息。")}</p>
  </section>;
}

function EvidenceCard({ item, onOpen, language = "en" }: { item: Evidence; onOpen?: () => void; language?: Language }) {
  const location = item.page_number ? pick(language, `Page ${item.page_number}`, `第 ${item.page_number} 页`) : item.paragraph_start ? pick(language, `Paragraphs ${item.paragraph_start}–${item.paragraph_end}`, `第 ${item.paragraph_start}–${item.paragraph_end} 段`) : pick(language, "Document", "文档");
  return <article className="evidence-card"><div><StatusPill value={item.freshness} language={language} /><span className={item.data_status.includes("synthetic") ? "source synthetic" : "source public"}>{item.data_status.includes("synthetic") ? pick(language, "Synthetic", "合成数据") : pick(language, "Verified official", "已验证官方来源")}</span></div><h3>{item.title}</h3><small>{location} · {pretty(item.version_status, language)}{item.section ? ` · ${item.section}` : ""}</small><p>{item.excerpt}</p><footer><span>{item.source_name}<br />{pick(language, "Published", "发布于")} {item.published_at || pick(language, "not stated", "未注明")}<br />SHA-256 {item.document_sha256?.slice(0, 12)}…</span><a href={item.locator_url || item.source_url} target="_blank" rel="noreferrer" onClick={onOpen}>{pick(language, "Open cited passage ↗", "打开引用原文 ↗")}</a></footer></article>;
}

function CompareView({ data, language }: { data: any; language: Language }) {
  if (!data) return <Loading language={language} />;
  const metricNames = ["annualized_return", "annualized_volatility", "maximum_drawdown", "expense_ratio", "liquidity_days"];
  const metadataRows: Array<[string, (item: Instrument) => string]> = [
    [pick(language, "Product / issuer", "产品 / 发行人"), item => `${item.instrument_type} · ${item.issuer}`],
    [pick(language, "Currency / region", "币种 / 地区"), item => `${item.currency} · ${item.region}`],
    [pick(language, "Largest exposures", "主要敞口"), item => Object.entries(item.sectors).sort((a, b) => b[1] - a[1]).slice(0, 2).map(([name, value]) => `${name} ${pct(value)}`).join(" · ")]
  ];
  return <section className="page-content"><div className="page-intro"><span className="eyebrow">{pick(language, "NO “BEST” RANKING", "不进行“最佳”排名")}</span><h2>{pick(language, "Compare differences, dates and assumptions.", "比较差异、日期与假设。")}</h2><p>{pick(language, "Return and risk figures below use fixed-seed synthetic series. Product metadata retains its own source status and date.", "以下收益与风险数字使用固定种子的合成序列；产品元数据保留各自的来源状态和日期。")}</p></div>
    <div className="comparison-table"><div className="table-row table-head"><div>{pick(language, "Dimension", "维度")}</div>{data.instruments.map((item: Instrument) => <div key={item.instrument_id}><strong>{item.symbol}</strong><span>{item.instrument_type}</span></div>)}</div>
      {metadataRows.map(([label, render]) => <div className="table-row" key={label}><div>{label}</div>{data.instruments.map((item: Instrument) => <div key={item.instrument_id}><span>{render(item)}</span><small>{pick(language, "as of", "截至")} {item.as_of}</small></div>)}</div>)}
      <div className="table-row"><div>{pick(language, "Risk level", "风险等级")}</div>{data.instruments.map((item: Instrument) => <div key={item.instrument_id}><RiskDots level={item.risk_level} language={language} /></div>)}</div>
      {metricNames.map(metric => <div className="table-row" key={metric}><div>{pretty(metric, language)}</div>{data.instruments.map((item: Instrument) => <div key={item.instrument_id}><MetricValue calculation={data.metrics[item.instrument_id][metric]} /><small>{pick(language, "as of", "截至")} {item.as_of}</small></div>)}</div>)}
    </div><div className="note-grid">{data.comparability_notes.map((note: string) => <p key={note}>{localizeText(note, language)}</p>)}</div></section>;
}

function PortfolioView({ data, language }: { data: any; language: Language }) {
  if (!data) return <Loading language={language} />;
  return <section className="page-content"><div className="page-intro"><span className="eyebrow">{pick(language, "SYNTHETIC PORTFOLIO", "合成投资组合")}</span><h2>{pick(language, "See concentration and exposure before conclusions.", "形成结论前，先检查集中度与风险敞口。")}</h2><p>{pick(language, "This is not a recommendation, allocation optimizer, VaR model or forecast.", "这不是投资建议、配置优化器、VaR 模型或预测工具。")}</p></div><div className="portfolio-grid">
    <article className="large-card"><span className="eyebrow">{pick(language, "RISK TOOLS", "风险工具")}</span>{data.calculations.map((item: Calculation) => <div className="portfolio-metric" key={item.metric}><div><small>{pretty(item.metric, language)}</small><MetricValue calculation={item} /></div><p>{item.assumptions.map((text: string) => localizeText(text, language)).join(" ")}</p></div>)}</article>
    <Exposure title={pick(language, "Sector exposure", "行业敞口")} values={data.sector_exposure} />
    <Exposure title={pick(language, "Region exposure", "地区敞口")} values={data.region_exposure} />
    <Exposure title={pick(language, "Currency exposure", "币种敞口")} values={data.currency_exposure} />
  </div></section>;
}

function Exposure({ title, values }: { title: string; values: Record<string, number> }) {
  return <article className="large-card"><span className="eyebrow">{title}</span><div className="bars">{Object.entries(values).sort((a, b) => b[1] - a[1]).map(([label, value]) => <div key={label}><span>{label}<b>{pct(value)}</b></span><i><em style={{ width: pct(value) }} /></i></div>)}</div></article>;
}

function EvidenceView({ documents, language }: { documents: any[]; language: Language }) {
  return <section className="page-content"><div className="page-intro"><span className="eyebrow">{pick(language, "SOURCE REGISTER", "来源登记册")}</span><h2>{pick(language, "Verified official originals and synthetic fixtures stay distinct.", "始终区分已验证的官方原文与合成样本。")}</h2><p>{pick(language, "Each official file records version, retrieval timestamp, byte size and SHA-256 checksum.", "每份官方文件都记录版本、获取时间、文件大小和 SHA-256 checksum；原文保持来源语言。")}</p></div><div className="source-register">{documents.map(document => <article key={document.document_id}><div><span className={document.data_status.includes("synthetic") ? "source synthetic" : "source public"}>{document.data_status.includes("synthetic") ? pick(language, "Synthetic fixture", "合成样本") : pick(language, "Verified official file", "已验证官方文件")}</span><small>{document.document_type}</small></div><h3>{document.title}</h3><p>{document.version || document.content}</p><footer><span>{document.document_id}<br />SHA-256 {(document.sha256 || document.checksum).slice(0, 14)}…</span><a href={document.source_url} target="_blank" rel="noreferrer">{pick(language, "Official source ↗", "打开官方来源 ↗")}</a></footer></article>)}</div></section>;
}

function AuditView({ events, language }: { events: any[]; language: Language }) {
  return <section className="page-content"><div className="page-intro"><span className="eyebrow">{pick(language, "APPEND-ONLY SESSION TRACE", "只追加的会话轨迹")}</span><h2>{pick(language, "Inspect what changed, what fired and what the model never controlled.", "检查状态如何变化、哪些规则被触发，以及模型从未控制的部分。")}</h2><p>{pick(language, "Audit records are in-memory for this local prototype and reset when the API restarts.", "本地原型的审计记录暂存在内存中，API 重启后会清空。")}</p></div>{events.length === 0 ? <div className="empty-state"><div>00</div><h3>{pick(language, "No session events", "暂无会话事件")}</h3><p>{pick(language, "Run a research trace first.", "请先运行一次证据追溯。")}</p></div> : <div className="timeline">{events.map(event => <article key={event.audit_id}><div className="timeline-dot" /><div><span>{new Date(event.timestamp).toLocaleString(language === "zh" ? "zh-CN" : "en")}</span><h3>{event.query}</h3><div><StatusPill value={event.outcome} language={language} /><code>{pretty(event.intent, language)}</code><code>{event.provider}/{event.model}</code></div><p>{pick(language, "Policy", "策略")}：{event.policy_hits.map((hit: any) => hit.rule_id).join(", ") || pick(language, "none", "无")}</p><p>{pick(language, "Evidence", "证据")}：{event.evidence_ids.join(", ") || pick(language, "none", "无")}</p><small>{event.audit_id} · prompt {event.prompt_version}</small></div></article>)}</div>}</section>;
}

function EvaluationView({ data, language }: { data: any; language: Language }) {
  if (!data) return <Loading language={language} />;
  if (data.status === "not_run") return <section className="page-content"><div className="empty-state"><div>QA</div><h3>{pick(language, "Evaluation not generated", "尚未生成评测")}</h3><p>{data.message}</p></div></section>;
  return <section className="page-content"><div className="page-intro"><span className="eyebrow">{pick(language, "REPRODUCIBLE EVALUATION", "可复现评测")}</span><h2>{pick(language, `${data.passed} of ${data.cases} deterministic cases passed.`, `${data.cases} 个确定性案例中 ${data.passed} 个通过。`)}</h2><p>{pick(language, `Seed ${data.seed}. These are synthetic regression cases, not real-user or production performance.`, `随机种子 ${data.seed}。这些是合成回归案例，不代表真实用户或生产表现。`)}</p></div><div className="eval-summary"><div><strong>{data.cases}</strong><span>{pick(language, "Cases", "案例")}</span></div><div><strong>{data.passed}</strong><span>{pick(language, "Passed", "通过")}</span></div><div><strong>{data.failed}</strong><span>{pick(language, "Failed", "失败")}</span></div></div>
    {data.baselines?.length > 0 && <section className="baseline-section"><div className="section-heading"><div><span className="eyebrow">{pick(language, "EXECUTED ABLATIONS", "已执行消融实验")}</span><h2>{pick(language, "Controls removed on relevant case slices", "在相关测试切片中移除控制模块")}</h2></div><span>{pick(language, "Not model benchmarks", "不是模型基准测试")}</span></div><div className="baseline-grid">{data.baselines.map((baseline: any) => <article key={baseline.name}><span>{pretty(baseline.name, language)}</span><strong>{baseline.passed}/{baseline.cases}</strong><p>{localizeText(baseline.definition, language)}</p><small>{localizeText(baseline.scope, language)}</small></article>)}</div></section>}
    <div className="metric-list">{data.metrics.map((metric: any) => <article key={metric.name}><div><span>{pretty(metric.name, language)}</span><strong>{pct(metric.value)}</strong></div><i><em style={{ width: pct(metric.value) }} /></i><p>{localizeText(metric.definition, language)}</p><small>{metric.numerator}/{metric.denominator}</small></article>)}</div>
    <article className="trend-note"><span className="eyebrow">{pick(language, "REGRESSION TREND", "回归趋势")}</span><strong>{pick(language, "One committed run", "当前仅有一次已提交运行")}</strong><p>{pick(language, "A trend is intentionally not inferred from a single snapshot. Preserve subsequent generated artifacts to compare changes over time.", "单次快照不能推断趋势；后续应保留生成结果，以比较系统随时间的变化。")}</p></article>
  </section>;
}

function Loading({ language = "en" }: { language?: Language }) { return <section className="page-content"><div className="empty-state"><div>…</div><h3>{pick(language, "Loading local evidence", "正在加载本地证据")}</h3></div></section>; }

export default App;
