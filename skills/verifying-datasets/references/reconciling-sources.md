# When two sources disagree

Two numbers for one thing is the normal condition, not an anomaly. The work is explaining the gap,
not closing it. A reconciliation that ends in "roughly the same" has not reconciled anything.

**Never average two numbers that disagree.** The average is a third number that no system produced
and nobody can defend. Never adopt the one that supports the decision. Both moves convert a
finding into a fabrication.

## Work down the causes in order

Most gaps are explained before the fourth step. Stop at the first cause that accounts for the size
of the gap, and check that it accounts for the *size* — a mechanism that explains 2% is not the
explanation for a 40% gap, and finding it is a common way to stop looking too early.

### 1. Population

Are the two counting the same things? This is the most common cause and the easiest to miss,
because both sources use the same word.

Ask what makes a row eligible in each: date of what event, which properties or accounts, which
statuses, which countries, which currencies, test and internal records included or not, and whether
a cancelled, refunded, deleted, or merged record still appears.

### 2. Window

Same period is not the same as the same rows.

- **Timezone.** A source reporting in the property's timezone and one reporting in UTC disagree
  about every day boundary, and the gap is largest at the edges of the range.
- **Extraction moment.** Two exports of one past period, taken days apart, will differ if the system
  accepts late or backdated data. Google documents that Analytics processing "can take 24-48 hours"
  and that during that time "data in your reports may change." A number is therefore a function of
  when you asked, and the extraction moment belongs in the return alongside the period.
- **Event time versus ingestion time.** A row can belong to Monday by one and Tuesday by the other.
- **Open periods.** A period that has not settled — refunds, disputes, and cancellations still
  arriving — is not comparable with a closed one.

### 3. Definition

The same noun is a different object in two systems. A session has a timeout rule and can be
restarted by a campaign parameter; an order may be created, paid, fulfilled, or settled; a lead may
be a form submission or a qualified record; a "user" may be counted per device.

Write both definitions down side by side. If you cannot state each system's definition, you cannot
reconcile them and should say so rather than proceeding.

### 4. Identity

Counting distinct things requires deciding what a thing is. Cookies, device identifiers, logged-in
accounts, hashed emails, and household keys produce different counts of "people" from identical
underlying events, and consent state changes which of them exists at all.

Distinct counts across two systems rarely reconcile exactly. Say by how much and why, rather than
implying a precision neither has.

### 5. Filtering

Rows removed by rules nobody applied deliberately:

- bot and internal-traffic exclusion, which differs per tool;
- consent and regional restrictions, which remove rows unevenly by geography;
- permission scope — an export can silently omit what the extractor could not see;
- sampling above a volume threshold, which produces an estimate rather than a count;
- thresholding, which withholds rows to protect individuals and is invisible in the output.

Thresholding deserves a specific check because it breaks breakdowns while leaving totals intact.
See `file-integrity.md` for what Google documents about withheld rows.

### 6. Arithmetic

Last, and least often the cause: duplicates inflating one side, currency mixing, rounding applied at
different stages, and joins that multiplied rows.

## Build the bridge

State the reconciliation as a ledger. Start at one source's number, apply each adjustment with its
size and its evidence, and land on the other's.

```text
Source A, orders, 2026-07, property timezone          4,812
  less test-mode records excluded by B                  -37
  less orders created but never paid                   -204
  plus orders paid in July, created in June             +91
  less currency rows B reports separately               -18
  unexplained residual                                  -12
Source B, paid orders, 2026-07, UTC                   4,632
```

Rules for the ledger:

- **Every line carries evidence.** A line you cannot demonstrate is a guess, and a guess in a
  reconciliation is worse than a residual.
- **The residual stays.** Report its size and its share. A residual under a stated tolerance is a
  reconciled result with a known limit; a residual you deleted is a fabricated result.
- **One direction only.** Bridging A to B and B to A with different adjustments means you have two
  stories, not a reconciliation.

## Aggregates reverse, and that is arithmetic

An association present in every subgroup can disappear or reverse in the combined population when
the subgroups differ in size — Simpson's Paradox. Both figures are correct; they answer different
questions.

The canonical case is Bickel, Hammel, and O'Connell's 1975 study of Berkeley graduate admissions:
men were admitted at a higher rate university-wide, yet the authors could not detect a bias toward
men in any individual department, because women applied in greater numbers to departments with lower
acceptance rates overall. The Stanford Encyclopedia of Philosophy's entry sets out the probabilistic
structure and why the aggregate does not establish what it appears to.

The practical rules:

- **Never conclude from an aggregate you have not decomposed.** Segment first, then decide which
  figure answers the question, then say which one you reported and why.
- **A rate comparison across groups of unequal size is the specific shape at risk.** Conversion rate
  by channel, by device, by country, and before-versus-after a mix shift are all this shape.
- **A change in the mix can move a total while every segment is flat.** Check that before attributing
  the movement to performance.

## Check that the parts sum to the whole

Do this on every breakdown. It is the cheapest test available and it catches:

- withheld or thresholded rows, where the breakdown is short of the total;
- double counting from a join on a non-unique key, where the breakdown exceeds it;
- an "(other)" or "(not set)" bucket doing more work than the analysis admits;
- rows excluded by a filter applied to the breakdown but not to the total.

When they do not sum, say so and name the gap's size before interpreting anything. An unexplained
difference between a total and its own breakdown invalidates the breakdown, not just the missing
rows.

## Comparing periods

- **Compare equal ages, not equal calendar spans**, whenever an observation matures — a cohort, a
  subscription, a lead that converts weeks later. Mark incomplete observations as censored rather
  than counting them as failures.
- **Weeks and months do not align**, and the drift compounds across a year.
- **Some fiscal years have 53 weeks.** The National Retail Federation's 4-5-4 calendar notes that
  52 weeks of seven days leaves an extra day each year, so "every five to six years a week is added
  to the fiscal calendar," most recently in FY12, FY17, and FY23. NRF publishes both restated and
  non-restated calendars for those years. Comparing an unrestated 53-week year with a 52-week
  neighbour overstates growth by roughly a week's trade.
- **Classification and schema revisions break series.** A definition that changed mid-series is a
  break to report, not a line to draw through.

## What to return

The reconciliation itself, in this order: both numbers with their full provenance; both definitions
stated side by side; the ledger with each adjustment and its evidence; the residual with its size
and share; and the statement of which number answers the question that was asked, with the reason.

When the gap cannot be explained, that is the result. Return both numbers, the causes ruled out and
how, and what access or definition would settle it. **An unexplained disagreement reported honestly
is a usable finding; a disagreement resolved by preference is not a finding at all.**
