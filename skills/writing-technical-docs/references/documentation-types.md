# Match the page to the reader's need

Use one dominant documentation type per page. Cross-link related types instead of forcing every
reader through one long narrative.

## Choose the type

| Reader need | Type | Shape |
|---|---|---|
| Learn by doing | Tutorial | Guided, controlled sequence that reaches a meaningful result. |
| Complete a known task | How-to | Prerequisites, direct steps, checkpoints, recovery, and next action. |
| Look up a contract | Reference | Accurate, complete facts organized like the interface being described. |
| Understand why or how | Explanation | Concepts, relationships, tradeoffs, and verified context. |
| Recover from failure | Troubleshooting | Exact symptom, verified cause boundary, safe diagnostic, correction, and proof. |

```text
Bad:  An endpoint reference pauses for a beginner lesson, then hides errors in architecture history.
Good: Keep the endpoint contract together; link a quickstart for the first call and an explanation
      for the domain model where each becomes relevant.
```

Do not create empty sections for all types. Add only the pages the audience needs.

## Give each audience an entry path

### Consumer or integrator

Answer:

- What problem does this solve, and is it the supported interface for my use case?
- What must exist before I start?
- What is the smallest successful call or workflow?
- What observable result proves success?
- What common failures can I diagnose and recover from?
- Which compatibility, security, cost, or operational limits affect use?

### Maintainer or contributor

Answer:

- Where are the public entry points and tests?
- Which components own the behavior, state, and external effects?
- Which invariants and compatibility promises must a change preserve?
- How is an extension registered, configured, tested, and removed?
- Which focused and broader checks prove a safe change?
- Where is rationale recorded when it actually exists?

## Write troubleshooting from symptoms

Use the text the reader can observe: an error code, log line, state, or missing result. For each
entry, provide:

1. the exact symptom and affected versions or environments;
2. the proven cause or the boundary the evidence narrows it to;
3. a safe diagnostic that distinguishes it from similar failures;
4. the corrective action and rollback where relevant; and
5. the signal that confirms recovery.

Do not turn one incident into a universal cause. If multiple causes share a symptom, give a decision
path and preserve uncertainty.
