# tokenomics — spend your tokens well 🪙

> Two open Claude skills for getting **better results for less**. Start simple:
> **[nail-it](nail-it/)** turns vague prompts into sharp ones. Go deep:
> **[tokenomics](tokenomics/)** measures your whole pipeline and ships a proven, cheaper
> config. Every rule is backed by a **real, measured study** — not vibes.

_MIT · domain-anonymized · every number is a real receipt at published Anthropic API rates._

## The 30-second version
Most people optimize the wrong thing. In a measured study on a real production LLM agent,
the #1 reflex — **reach for a bigger model** — was the **least** useful lever. What actually
worked was dull and free: **say exactly what you want**, and **stop re-reading context you
don't need.** These two skills package that so you don't have to run the study yourself.

## Pick your tier

| Skill | For | What it does | Setup |
|---|---|---|---|
| 🎯 **[nail-it](nail-it/)** | everyone | Rewrites a vague prompt into a specific one — audience, length, checkable success criteria, right-sized model — asking a question only when it must. | **one file, 30s** |
| 🔬 **[tokenomics](tokenomics/)** | pipeline builders | A measurement harness: open the black box, apply cost levers in the proven order, judge-gate every change, ship a config **with receipts**. | Python + your pipeline |

Most people want **nail-it**. Reach for **tokenomics** when you run a real pipeline and want
to *prove* a cheaper config holds quality.

## Install (30 seconds)
```bash
cp -r nail-it     ~/.claude/skills/     # the simple one — start here
cp -r tokenomics  ~/.claude/skills/     # the advanced harness
```
(Per-project: use `.claude/skills/` instead.) Then just talk to Claude — e.g.
`/nail-it write me a landing page`, or let nail-it tighten loose prompts automatically.

## Before → after (nail-it)
**Before:** "write me something about our new feature for the blog"

**After:** "Write a 600-word blog post announcing **<feature>** for technical users new to
**<domain>**. Lead with the problem it solves, show one before → after, end with one call to
action. Name the feature in the first line; include one real usage example. Concrete, no
fluff."

Same idea — the first draft is the one you wanted. Fewer correcting turns, fewer tokens.

## The receipts (why trust the rules)
From a measured study on a real long-form-content agent (full numbers in
[`tokenomics/examples/`](tokenomics/examples/README.md)):

- **Context architecture** cut re-read tokens **~5×** *before any model change* — a
  32–63× smaller per-call instruction payload.
- **Tightening the spec** lifted a **cheap and an expensive** model to the *same* score —
  the model was never the bottleneck.
- **The flagship model lost.** It was the baseline ($5.22/run, 4/5); a mid-tier model at
  high effort beat it — **~$1.01 and 5/5**. Across everything measured, the flagship wasn't
  needed anywhere.
- **"Caveman" lexical compression** saved ~nothing once context was lean — and cost a
  quality point. The win is structural, not lexical.

> **The order that pays off:** context architecture → spec & eval → effort → model tier →
> (maybe) lexical. Most teams start at "bigger model." In the data that was last and least.

## How it works
- **nail-it** is a single `SKILL.md` — no code, no deps. It rewrites loose requests using
  the measured rules before they run.
- **tokenomics** is a small Python harness (`rates · observe · judge · ab · validate`) plus
  the 10 rules and the receipts. From its folder, run `python -m engine.validate` to prove
  the harness, then follow its [`SKILL.md`](tokenomics/SKILL.md).

## License
MIT. The findings are real, measured receipts computed at published Anthropic API rates.
If it helps you, a ⭐ helps others find it.
