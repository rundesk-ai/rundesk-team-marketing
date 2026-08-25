# Certifying value

"What was it worth" is four different numbers, and the gap between them is larger than most of the
effects anyone is trying to measure. Certifying value means naming which one you are reporting and
reconciling it to the system that accepted the money or the lead — not converting an analytics
revenue figure into a business claim.

## Analytics revenue is a report of what the tag sent

A web or product analytics property holds the value its instrumentation reported at the moment of an
event. It is a measurement of the tag, not of the ledger. It is missing everything that happened
afterwards and everything that never reached it: failed and retried payments, manual and offline
orders, partial fulfilment, refunds, disputes, fees, tax, shipping, and every transaction where the
tag did not fire or consent was withheld.

Use it to compare periods and segments within the same instrumentation. Do not release it as a
value claim without reconciling it to the payment or order system. When no such system is reachable,
the value is unestablished — say that rather than reporting the analytics figure with a caveat
attached.

## The four numbers, in the order they diverge

1. **Money movement** — what the payment processor recorded moving, grouped by type. Includes fees,
   refunds, adjustments, and transfers. Not revenue.
2. **Money held or paid out** — a balance is what the processor currently holds; a payout is the
   transfer to a bank account. Neither is a period's sales.
3. **Invoiced or booked amount** — what was billed, before anything reverses.
4. **Recognized revenue** — the accounting figure. Stripe's documentation states the principle
   plainly: GAAP requires revenue to be recognized "when you realize and earn it, which might be
   earlier or later than when you actually receive payments." An annual subscription collected in
   January is not January revenue.

Marketing questions usually want (3) adjusted for reversals; finance questions usually want (4).
They are not interchangeable, and quoting one to answer the other is the most common way a
certified number turns out to be wrong.

## The period is not closed when the period ends

An apparent conversion can reverse long after you counted it.

- **Refunds and cancellations** arrive on their own schedule.
- **Disputes reverse a booked sale and add a fee.** Stripe documents that when a cardholder disputes
  a charge, it "debits the disputed amount, plus a dispute fee, from your Stripe account," and that
  the outcome rests with the cardholder's bank rather than with the merchant or the processor. The
  filing window is set by the card networks and varies, so a recent period's value is provisional
  for longer than the reporting calendar suggests.
- **Fraud warnings precede disputes.** A charge flagged by an issuer may or may not become a
  dispute; treating a warning as a reversal double-counts, and ignoring it understates.

Two consequences for a metric contract:

- **State the settlement maturity**, not only the period. "July, as at 20 August, with disputes still
  open" is a certifiable statement; "July revenue" is not.
- **Never compare a fresh period against a matured one.** A recent month always looks better than an
  older one because its reversals have not landed yet, and that difference is not performance.

## Check the mode before quoting any figure

Payment systems have test environments that return fully-formed, entirely fictional balances,
charges, and payouts. Establish which environment produced a figure before it enters an analysis,
and say so whenever it is not the live one. A number sourced from test data and reported as revenue
is a fabrication regardless of how carefully it was computed.

Where several accounts or profiles exist, they are usually separate businesses or separate legal
entities. Reporting one account's figures as another's is worse than returning nothing, so select
the account explicitly rather than defaulting to whichever was configured first.

## Currency

Keep the currency with the amount at every step. A total that sums mixed currencies is meaningless.
Converting requires a stated rate and a stated date, and both belong in the return. Amounts held in
minor units are not all hundredths — several currencies have no minor unit at all and a few use
three decimal places — so a blanket division to convert them corrupts those rows silently. See
`verifying-datasets` for the arithmetic-level checks.

## Attribution window and settlement date are different clocks

A conversion attributed to a July campaign may settle in August, be refunded in September, and be
recognized across twelve months. Fix which clock the analysis runs on and use it consistently:

| Clock | Answers | Use for |
|---|---|---|
| Interaction date | when the marketing happened | Channel comparison within one instrumentation |
| Conversion date | when the outcome occurred | Funnel and conversion-rate work |
| Settlement date | when money actually moved | Reconciliation to the payment system |
| Recognition period | when revenue is earned | Accounting-comparable figures |

Mixing them produces a number that reconciles to nothing. Attribution still assigns reporting credit
under a model and still does not establish causal effect; adding money to it does not change that.

## Lead outcomes have their own chain

Where the outcome is a lead rather than a purchase, each stage is a different population with a
different denominator and usually a different owner:

```text
submitted → deduplicated → valid contact → reached → qualified → opportunity → won → retained
```

A conversion rate is meaningless until it names which two stages it spans. Rejection,
disqualification, duplication, and unreachability are outcomes to count, not noise to drop — a
campaign that doubles submissions and halves qualification has not improved. Where the later stages
live in a system the analysis cannot reach, say which stage is the last one established and treat
everything downstream as unmeasured rather than assumed proportional.

## Lifetime value is a forecast

Realized value to date is a measurement. Lifetime value is a projection about cohorts that have not
finished, and it inherits every requirement in `forecasting-and-uncertainty.md`: a backtest against
a naive baseline, an interval, a horizon, and a statement of what it is not. Report realized value
with its observation window and mark the cohorts still open as censored. A single LTV figure with no
horizon and no interval is a target wearing a measurement's clothes.
