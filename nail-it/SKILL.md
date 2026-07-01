---
name: nail-it
description: >-
  Turn a vague request into a tight, specific prompt before it runs, so the first result is
  the one you wanted. Use whenever a prompt or task is loose, ambiguous, or under-specified:
  nail-it pins down audience, output shape and length, explicit success criteria, scope, and
  the right model/effort — asking a quick question only when something essential is genuinely
  unknowable. Trigger on /nail-it, "nail it", "tighten this prompt", "sharpen this", or
  whenever a request is clearly under-specified.
---

# nail-it — pin down what you actually want

Vague prompts get vague results, and you pay for the vagueness twice: once in a mediocre
first answer, and again in the back-and-forth to fix it. `nail-it` rewrites a loose request
into a specific one *first*. The rules it applies aren't opinion — they're the ones that
moved real numbers in a measured study (see the repo's receipts).

## When to act
Fire when the request is under-specified, or when the user invokes you explicitly. Signs of
under-specification: no stated audience, no length or format, success stated as adjectives
("good", "compelling", "clean"), several goals crammed into one ask, or a bare "write / make
/ build me X" with little else.

## Two modes
- **Silent (default).** When a request is loose, quietly tighten it and proceed with the
  tightened version. Don't announce it or slow the user down.
- **Preview (`/nail-it …` or a `nail-it:` prefix).** Output the tightened prompt *as text*
  for the user to read and copy. Do **not** execute it. Show a one-line before → after.

## Ask before you guess — but only when it matters
If an *essential* dimension is genuinely unknowable and would change the output a lot, ask
**1–3 crisp questions** first (audience? length? the one must-have?). Otherwise pick a
sensible default, state it in one line, and proceed. Never interrogate the user for things
you can reasonably infer. One good question beats five lazy ones.

## The tightening checklist (apply it, don't recite it)
Rewrite the request so it pins down:
1. **Audience & level** — who it's for and what they already know, so depth matches
   (mechanism for an expert; plain consequence for a beginner — same topic, different bar).
2. **Output shape & length** — the format, plus a concrete target ("~400 words", "5
   bullets", "a 30-line function"), and an instruction to actually hit it.
3. **Success as checkable steps** — turn adjectives into criteria the model can verify:
   "must include X", "exactly N items, none overlapping", "cite each claim", "runs as-is".
4. **Scope & non-goals** — one clear job; say what *not* to do.
5. **Right-size the model & effort** — suggest the cheapest model that holds the bar and a
   sensible effort; recommend a bigger model or higher effort only for genuinely hard or
   dense tasks. Don't reach for the flagship by reflex — in the study it was the *least*
   useful lever.
6. **Stay lean** — keep the rewrite tight. Specificity, not padding.

## Output format (preview mode)
```
Tightened prompt:
<the rewritten, specific, copy-pasteable prompt>

Assumed (only if you defaulted anything): <one line>
```

## Example
**Before:** "write me something about our new feature for the blog"

**After:** "Write a 600-word blog post announcing **<feature>** for existing users who are
technical but new to **<domain>**. Lead with the problem it solves, show one concrete
before → after, and end with a single call to action. Must name the feature in the first
line and include one real usage example. Friendly and concrete — no marketing fluff."

That's it — one file, no setup. Point Claude at a loose request and it comes back sharp.
