# RULES — the optimization playbook (operationalized)

> The skill applies these in order, judge-gating each step. Generic "content-generation agent" framing.

## Phase 0 — Open the black box (measure the baseline)
- Capture, per call: input/output tokens, **cache-read vs cache-creation**, num turns, **per-model
  usage** (which model did the work, how hard), wall time, cost.
- Identify the **per-turn context × turn-count** product. This is almost always where the money is, and
  most teams have never measured it.

## Phase 1 — Context architecture (biggest lever)
- Stop re-reading large always-on docs every turn. Give the agent **one small, self-contained spec per
  task**, read once. Target ≥30× smaller per-call doc payload.
- Keep static context byte-identical so it's cache-read, not re-created.
- Trim the tool surface to what the task needs.
- **Gate:** quality must hold vs baseline; cost/cache should drop sharply.

## Phase 2 — Spec + eval (where quality actually lives)
- Build a **cheap automated judge** first (a small model, 1–5 rubric). Make the rubric **audience-matched**
  — judge each artifact against *its* reader, never a fixed bar.
- When output is weak, **tighten the spec, don't upsize the model.** Encode acceptance criteria as steps
  the model executes (a length gate; a "list sub-areas, dedupe" diversity check; a depth-matches-tone
  rule), not hopes in the preamble.
- **Gate:** judge ≥ target on the tightened spec, same model.

## Phase 3 — Effort
- Sweep reasoning effort low→high on the (now cheaper) model; find the knee. Effort is a free dial that
  often removes the need for a dearer model.
- Optional: a structured plan→expand→self-check scaffold can lift a *lower* effort tier to top quality —
  but budget for extra orchestration turns; it's a quality lever, not reliably a cost one.

## Phase 4 — Model tier (only now)
- Right-size per task: cheapest model that holds the bar. Reserve the expensive model for where it
  *measurably* wins.
- **Tier within a task, don't blanket-upgrade:** default cheap; add a cheap detector (e.g. "are the N
  outputs distinct?", "did it hit length?") and escalate only the failing cases to a stronger model.
- **Gate:** judge ≥ target at the new (lower) cost.

## Phase 5 — (maybe) lexical / micro
- Only after the above. Compressing the *wording* of an already-lean, read-once spec saves ~nothing and
  risks the nuanced rules — measure before adopting; usually skip.
- Never compress the **deliverable** when the content *is* the product.

## Cross-cutting discipline
- **Validate the harness before trusting any number** (unique scratch paths, full-length judge input,
  defensive parsing, log raw runs, confirm you're judging the *fresh* artifact).
- **One variable per experiment**; repeat where variance matters; a TEST artifact (e.g. a fixed target
  length on the wrong topic) is not a content failure — diagnose, don't floor.
- **Never compromise an audience:** if a segment scores low, first check the eval matches it, then fix
  the spec; lift every audience to the same bar.

## Output
A recommended **per-pipeline config** (model, effort, lean-doc) with the before→after cost + quality
proof, the projected per-op token/cost reduction, and the capacity (e.g. "Nx more users per fixed
budget"). Plus the self-improving loop that re-runs the gate as the workload evolves.
