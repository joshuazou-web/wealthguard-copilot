# Two-week real-use validation

## Decision to test

The product is an **evidence-grounded research protection layer**, not an investment companion.
The current hypothesis is that a mobile-friendly web app is sufficient. A native WeChat mini
program should be built only if repeated real use demonstrates an entry, notification, or sharing
problem that the web product cannot solve.

## Daily protocol

For 14 consecutive calendar days, use WealthGuard only when a genuine wealth or securities
research question occurs. Do not manufacture sessions to improve the numbers.

1. Record the question as it naturally occurred.
2. Run the trace and answer any clarification only if comfortable doing so.
3. Open at least one cited passage when the conclusion affects further research.
4. Mark the trace `Useful` or `Needs work`.
5. Record a mini-program signal only at the moment one of these frictions actually occurs:
   `Faster entry`, `Notifications`, or `WeChat sharing`.
6. Export the browser-local JSON at the end of days 7 and 14.

Do not enter account numbers, identity documents, exact holdings, transaction records, addresses,
or other sensitive financial information. The browser log is a usability study, not a suitability
record and not regulated customer data.

## Measures

- Active days: distinct calendar days on which the web app was opened.
- Research traces: genuine questions submitted.
- Evidence-open rate: traces with at least one exact source passage opened / all traces.
- Feedback coverage: rated traces / all traces.
- Useful-trace rate: `Useful` ratings / rated traces.
- Repeat correction themes: manually grouped reasons behind `Needs work`.
- Mini-program signals: contemporaneous entry, notification, and sharing needs—not hypothetical preference.

These are single-user product-discovery observations. They are not adoption, retention, conversion,
or production-quality metrics and must not be represented as such.

## Day-14 decision rule

Continue with the responsive web product unless all of the following are true:

1. The product was used on at least 7 of 14 days and produced at least 10 genuine traces.
2. At least 3 separate sessions produced the same mini-program-specific friction.
3. That friction is central to the evidence-protection workflow and cannot be solved credibly with
   a home-screen PWA, a bookmark, or an ordinary web notification/share flow.

If the rule is met, prototype only the smallest mini-program surface that removes the demonstrated
friction. Do not reproduce the entire research workspace.

## Day-14 review questions

- Which real questions could not be answered with the current official corpus?
- Where did the evidence trail change or restrain the user's initial conclusion?
- Which clarification questions were unnecessary or missing?
- Which citations were opened, and which were trusted without inspection?
- Which `Needs work` cases reveal a retrieval, policy, freshness, or interaction problem?
- Was WeChat-native access truly required, or merely familiar?
