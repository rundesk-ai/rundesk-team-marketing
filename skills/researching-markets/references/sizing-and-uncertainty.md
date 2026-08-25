# Building an estimate and reporting its uncertainty

## Three ways to reach a number

**Bottom-up.** Count buyers, multiply by purchase rate and price. Every factor is separately
checkable and separately arguable, which is the point. Prefer this.

**Top-down.** Start from a counted broader total and take a share of it. Fast, and only as good as the
share assumption — which is usually the whole answer wearing a percentage sign. Legitimate as a
**cross-check** on a bottom-up build; weak as the primary method.

**Value-based.** Estimate what the problem costs buyers today and what fraction they would pay to
solve it. Useful when no category exists yet and there is nothing to count. Highly assumption-laden;
label it as such.

The failure mode of top-down is not arithmetic, it is the assumption that the future resembles the
past. A published estimate of Uber's addressable market anchored on the historical taxi and limousine
market — about $100 billion globally, built up with every assumption stated — was answered by an
investor's rebuttal arguing that anchoring on the existing market assumes a product like Uber has
zero effect on the size of the market it enters. **Same framework, competent analysts on both sides,
roughly 25× apart.** The disagreement was entirely about boundary and share.

Two practices from that exchange are worth copying exactly. The analyst wrote that what followed was
his estimate of value, not the true value, and flagged that his own share assumption sat at the
optimistic end. The rebutter disclosed that he was an investor and board member of the company he was
defending, then made the argument anyway. **Disclose the interest, state every assumption, publish
the arithmetic so someone else can move one input.**

That exchange also produced the sentence to keep at the front of your mind: hard numbers give a false
sense of security, and there is a critical difference between precision and accuracy. A model can
return a figure to two decimal places while resting on assumptions that move the answer by an order
of magnitude.

## Where uncertainty comes from

Metrology distinguishes two kinds, and the distinction maps exactly onto market sizing:

- **Type A** — derived from repeated observation and an observed frequency distribution. In practice:
  the counted inputs, whose publisher states their sampling error.
- **Type B** — derived from an assumed distribution based on degree of belief, evaluated by scientific
  judgement using all available information: prior data, general knowledge of the behaviour of the
  thing being estimated, specifications, and uncertainties assigned to reference data.

Both are legitimate. A judged input is not a defect — an unlabelled judged input is. Say which of
your factors are counted and which are believed.

**The rule that matters most here: do not double-count uncertainty components.** Citing three
published figures that all copied one another does not triangulate anything; it inflates confidence
from a single unverified source. Before treating two sources as independent, establish that they are.

## Report a range, not a point

Cost-estimating practice in public audit is blunt about this: high-quality estimates fall within a
range, the point estimate sitting between best and worst case. Analysts who fail to address
uncertainty produce point estimates that tell a decision-maker nothing about their likelihood, or
worse, carry confidence levels that are meaningless because nobody understood the arithmetic behind
them.

So:

- Give a **range**, and say what drives its width.
- Run a **sensitivity check**: name the one or two assumptions that move the answer most, and by how
  much. If a single judged share swings the result threefold, that is the finding.
- **Cross-check with a second method** and then examine the difference. Do not average two estimates
  into a midpoint — reconcile them, and if you cannot, report both with the reason they disagree.
- Keep an **assumptions log**: each assumption, its source, its quantified effect, its reliability,
  when and why it was made, and who accepted it. Public-sector analytical guidance treats this as a
  required artifact rather than a courtesy, and it is what makes an estimate auditable months later.

## TAM, SAM, SOM

No standards body, regulator, or foundational paper defines these terms. They are venture-capital and
startup-textbook convention that hardened through repetition. There is no authoritative definition to
appeal to and no established method behind the acronyms.

Use them when the requester does, and then:

- **Define each one in the answer.** Without a stated boundary the three labels are decoration.
- Do not let the framework imply rigor. Three labelled tiers are three assumptions, not a method.
- When a company states its own total addressable market, record it as the company's claim. Hundreds
  of annual reports use the phrase, which makes it genuine disclosure language and also an interested
  party's estimate of its own opportunity.

If a genuinely academic route is wanted for adoption over time rather than a static size, diffusion
modelling of new-product growth is the established literature — but it answers a different question,
and this package does not carry a verified treatment of it.

## The output contract

Every size answer states, in this order: the boundary; the number as a range; the method; each input
with counted-or-assumed marked; the cross-check and what the difference was; the sensitivity; and what
could not be established. An estimate missing the boundary or the assumptions is not reviewable, and
an unreviewable estimate is the kind that ends up in a board deck unchallenged.
