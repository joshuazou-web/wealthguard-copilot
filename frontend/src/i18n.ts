export type Language = "en" | "zh";

export function pick(language: Language, english: string, chinese: string) {
  return language === "zh" ? chinese : english;
}

const VALUES: Record<string, string> = {
  research: "资料研究",
  compare: "产品比较",
  portfolio_analysis: "组合分析",
  personalised_advice: "个性化建议请求",
  trade_execution: "交易执行请求",
  informational: "资料研究",
  clarification_required: "需要澄清",
  educational_only: "仅限教育研究",
  caution: "谨慎使用",
  refuse: "拒绝",
  human_review: "需要人工协助",
  current: "当前资料",
  review_date: "需复核日期",
  stale: "资料陈旧",
  future_dated: "日期异常",
  investment_horizon: "研究期限",
  liquidity_need: "流动性需求",
  loss_tolerance: "亏损容忍度",
  investment_experience: "投资经验",
  product_knowledge: "产品知识",
  concentration_preference: "集中度偏好",
  currency_exposure: "币种敞口",
  information_preference: "说明方式",
  under_1_year: "一年以内",
  "1_to_3_years": "1–3 年",
  "3_to_5_years": "3–5 年",
  over_5_years: "5 年以上",
  within_days: "数日内",
  within_months: "数月内",
  flexible: "时间灵活",
  very_low: "极低",
  low: "低",
  moderate: "中等",
  high: "高",
  very_high: "极高",
  none: "无",
  beginner: "初学者",
  intermediate: "中级",
  advanced: "高级",
  limited: "有限",
  working: "基本掌握",
  avoid_concentration: "避免集中",
  neutral: "中性",
  accept_concentration: "接受集中",
  home_currency_only: "仅本币",
  limited_foreign: "有限外币",
  accept_foreign: "接受外币",
  plain_language: "通俗说明",
  balanced: "平衡说明",
  technical: "技术说明",
  not_classified: "尚未分类",
  annualized_return: "年化收益率",
  annualized_volatility: "年化波动率",
  maximum_drawdown: "最大回撤",
  expense_ratio: "费用率",
  liquidity_days: "流动性天数",
  period_return: "区间收益率",
  fee_impact: "费用影响",
  filing_ratios: "财报比率",
  portfolio_concentration: "组合集中度",
  portfolio_annualized_volatility: "组合年化波动率",
  portfolio_maximum_drawdown: "组合最大回撤",
  simple_scenario_loss: "简单情景损失"
  ,financial_report: "财报解读"
  ,announcement: "公告问答"
  ,security_comparison: "证券比较"
  ,fixed: "已修复"
  ,triaged: "已分诊"
  ,regression_added: "已加入回归"
  ,blocked_release: "阻止发布"
};

export function displayValue(value: string, language: Language) {
  if (language === "zh" && VALUES[value]) return VALUES[value];
  if (language === "zh" && value.includes(".")) {
    const [prefix, metric] = value.split(".", 2);
    if (VALUES[metric]) return `${prefix} · ${VALUES[metric]}`;
  }
  return value.replaceAll("_", " ").replace(/\b\w/g, letter => letter.toUpperCase());
}

const TEXT: Record<string, string> = {
  "When might you need this money: within a year, 1–3 years, 3–5 years, or later?": "你可能何时需要使用这笔资金：一年内、1–3 年、3–5 年，还是更晚？",
  "How quickly might you need access to the money: days, months, or is timing flexible?": "你可能需要多快动用这笔资金：数日、数月，还是时间灵活？",
  "For this research, which loss range would make you stop and reassess: very low, low, moderate, high, or very high?": "在本次研究中，多大亏损幅度会让你停止并重新评估：极低、低、中等、高还是极高？",
  "How familiar are you with market-traded products: none, beginner, intermediate, or advanced?": "你对场内交易产品的熟悉程度如何：不了解、初学、中级还是高级？",
  "How well do you understand this product type: limited, working, or advanced knowledge?": "你对该产品类型的了解程度如何：有限、基本掌握还是深入了解？",
  "Should the analysis flag concentrated positions aggressively, neutrally, or only at high levels?": "分析应积极提示集中风险、中性提示，还是只在高度集中时提示？",
  "Should the analysis avoid, limit, or simply disclose foreign-currency exposure?": "分析应避免、限制还是仅披露外币敞口？",
  "Would you prefer a plain-language, balanced, or technical explanation?": "你希望获得通俗、平衡还是技术性的说明？",
  "The prototype cannot place, route or execute a trade.": "该原型不能下单、路由或执行任何交易。",
  "Guaranteed or loss-free investment claims are not supported.": "系统不支持保本、稳赚或收益保证类请求。",
  "Instructions to bypass product safeguards are rejected.": "系统拒绝绕过产品安全限制的指令。",
  "The system does not expose account credentials or sensitive personal data.": "系统不会披露账户凭据或敏感个人数据。",
  "The request is reframed from a personal recommendation to evidence-based research.": "该请求已从个性化推荐重构为基于证据的研究任务。",
  "A high-value clarification is required before personalised framing.": "在进行个性化研究表达前，需要先完成一个高信息价值澄清。",
  "The supplied research context conflicts with one or more product characteristics.": "提供的研究背景与一个或多个产品特征存在冲突。",
  "The system can provide education and sourced research, not personalised investment advice.": "系统可以提供教育信息和有来源的研究，但不提供个性化投资建议。",
  "The request is within the educational research boundary.": "该请求位于教育与资料研究边界内。",
  "Research profile is a prototype aid, not a regulatory suitability determination.": "研究档案只是原型辅助信息，不是监管意义上的适当性认定。",
  "Displayed price histories and portfolios are deterministic synthetic fixtures.": "展示的价格序列和投资组合均为确定性合成样本。",
  "At least one source requires a date check before current use.": "至少一项资料在用于当前研究前需要复核日期。",
  "Some evidence cards are explicitly synthetic product fixtures.": "部分证据卡明确标记为合成产品样本。",
  "Conflicting source facts require human date and version review.": "来源事实存在冲突，需要人工复核日期和版本。",
  "Invalid generated citations were removed before display.": "无效的生成引用已在展示前移除。",
  "I do not have enough validated evidence to answer.": "当前没有足够的已验证证据支持回答。",
  "I do not have enough dated evidence to answer this research question.": "当前没有足够带日期的证据支持回答该研究问题。"
  ,"Synthetic return, volatility and drawdown series support calculation testing only.": "合成收益、波动和回撤序列仅用于验证计算工具。"
  ,"Instrument types, currencies, risks and source dates differ; no overall best product is inferred.": "产品类型、币种、风险和来源日期不同，因此不推断总体上的最佳产品。"
  ,"Expense ratios can omit transaction, tax, spread, advice and other costs.": "费用率可能不包含交易、税费、价差、投顾及其他成本。"
  ,"Illustrative monthly price series generated with a fixed seed.": "使用固定种子生成的示例月度价格序列。"
  ,"The result is not the instrument's historical or forecast performance.": "结果不代表该标的的历史或预测表现。"
  ,"Twelve periods per year are assumed.": "假设每年包含 12 个周期。"
  ,"Static weights and fixed-seed synthetic monthly series.": "使用静态权重和固定种子的合成月度序列。"
  ,"No rebalancing, costs, cash flows, or historical-performance claim.": "不包含再平衡、成本、现金流，也不声称历史表现。"
  ,"This is not a forecast or a complete portfolio risk model.": "这不是预测，也不是完整的投资组合风险模型。"
  ,"Holding weights are synthetic and sum to one.": "持仓权重为合成数据且合计为 1。"
  ,"Every emitted citation identifier existed in the source register.": "每个输出的引用标识都存在于来源登记册中。"
  ,"A research answer included both evidence and cited claims.": "研究回答同时包含证据和带引用的结论。"
  ,"Every claim was cited or explicitly marked synthetic.": "每条结论都有引用，或被明确标记为合成内容。"
  ,"Share of emitted claims with unknown or empty citations.": "引用未知或为空的输出结论占比。"
  ,"Displayed core metrics matched independent deterministic recomputation.": "展示的核心指标与独立确定性重算结果一致。"
  ,"Evidence marked review-date/stale/future produced a date limitation.": "需复核日期、陈旧或未来日期的证据均触发日期限制。"
  ,"Restricted cases incorrectly returned an informational outcome.": "受限制案例被错误返回为普通信息结果的比例。"
  ,"Invalid model citations were removed and the service abstained.": "无效模型引用被移除，系统正确弃权。"
  ,"Execution, guarantee, bypass and sensitive-data requests were refused.": "交易执行、收益保证、绕过限制和敏感数据请求均被拒绝。"
  ,"Explicit attempts to bypass policy were refused.": "明确绕过策略的尝试均被拒绝。"
  ,"Cases passing every assertion for their category.": "通过所属类别全部断言的案例。"
};

export function localizeText(text: string, language: Language) {
  if (language === "en") return text;
  if (TEXT[text]) return TEXT[text];
  if (text.startsWith("Research view only")) return "仅限资料研究：以下结论直接来自所列原始资料。请结合文件日期、具体引用和限制条件复核后再作判断。";
  if (text.startsWith("Possible answers change ")) {
    const paths = text.match(/change (\d+) policy path/)?.[1] || "多个";
    const bits = text.match(/has ([\d.]+) bits/)?.[1] || "较高";
    return `可能的回答会改变 ${paths} 条策略路径；该字段包含 ${bits} bits 的未解决信息。`;
  }
  if (text.startsWith("Additional context could materially change")) {
    return `补充信息可能实质性改变安全研究边界：${text.split(":").slice(1).join(":").trim()}`;
  }
  return text;
}
