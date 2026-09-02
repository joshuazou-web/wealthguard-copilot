# Deterministic calculation methods

## General rules

- Inputs must be finite and structurally valid; missing data is never imputed.
- Price series must contain at least two positive values.
- Portfolio and exposure weights must be non-negative and sum to one within `1e-6`.
- Incompatible lengths or invalid frequency assumptions raise an error.
- Money-oriented fee outputs use `Decimal` and round half-up to two decimal places.
- Every API result carries its formula, assumptions, unit, and provenance status.
- Language models do not calculate or overwrite these values.

All price paths in the demo are fixed-seed synthetic monthly series. They are used to test
arithmetic and user-interface behaviour, not to describe past or future investment performance.

## Metrics

### Period return

`R = P_last / P_first - 1`

Requires two or more positive prices. No cash flow, dividend, split, currency, tax, or fee
adjustment is inferred.

### Annualised return

`R_annual = (P_last / P_first) ** (periods_per_year / observed_periods) - 1`

The demo assumes 12 periods per year. It is a geometric annualisation of endpoints, not an IRR.

### Annualised volatility

`vol_annual = sample_stdev(periodic_returns) × sqrt(periods_per_year)`

Returns use adjacent price ratios. With fewer than two periodic returns, volatility returns zero
because dispersion is not observable in the fixture.

For the synthetic portfolio view, each instrument path is normalised to one and combined using
static holding weights before the same volatility and drawdown functions are applied.

### Maximum drawdown

`MDD = min(P_t / running_peak_t - 1)`

The output is zero or negative. It uses the observed fixture path only.

### Fee impact

`without_fee = principal × (1 + gross_return) ** years`

`with_fee = principal × (1 + gross_return - annual_fee) ** years`

`fee_drag = without_fee - with_fee`

The demo assumes a constant return and fee, annual compounding, and no taxes, trading costs,
spreads, advice fees, cash flows, or changing schedules.

### Concentration

- Largest position: `max(weight)`
- Top-three share: sum of the three largest weights
- Herfindahl index: `sum(weight ** 2)`

These describe concentration; they do not recommend a target allocation.

### Sector, region, and currency exposure

`portfolio_exposure[label] = sum(holding_weight × instrument_exposure[label])`

Each instrument exposure map and the holding weights must sum to one. Missing labels contribute
zero; missing maps are not invented.

### Simple scenario loss

`portfolio_change = sum(weight × shock)`

The UI example scales one declared base shock linearly by a synthetic 1–5 risk level. This is an
illustration, not VaR, expected shortfall, certified stress testing, or a forecast.

### Selected filing ratios

- Revenue growth: `current_revenue / previous_revenue - 1`
- Component share: `component_revenue / current_revenue`

The current fixture uses selected, dated Apple Form 10-K amounts. The code rejects non-positive
total revenues and a component greater than total revenue.

### Comparison normalisation

For a metric shared by all rows:

`score = (value - min) / (max - min)`

The score is inverted for a declared lower-is-better metric. Equal values receive `0.5`. This
normalisation supports charts only and must not be used to produce an overall product rank.

## Test coverage

`tests/test_calculations.py` covers expected results and boundaries including insufficient prices,
non-positive values, invalid weights, exposure sums, shock limits, negative inputs, and comparison
ties. The evaluation runner independently recomputes core metrics rather than trusting the service
payload.
