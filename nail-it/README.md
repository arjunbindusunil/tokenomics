# nail-it 🎯 — turn vague prompts into sharp ones

> Vague prompt in, vague answer out. `nail-it` rewrites a loose request into a specific one
> *before* it runs — so the first result is the one you wanted, not the third.

One file. No setup. No dependencies.

## Install (30 seconds)
```bash
cp -r nail-it ~/.claude/skills/         # global
# or, per project:
cp -r nail-it .claude/skills/
```

## Use it
- **Just talk.** When your ask is loose, nail-it quietly tightens it and runs the sharp
  version. If something essential is missing, it asks one quick question instead of guessing.
- **Preview a rewrite:** `/nail-it write me a landing page` → it hands back a tightened,
  copy-pasteable prompt *without* running it.

## What it pins down
Audience & level · output shape & length · success criteria as *checkable steps* (not
adjectives) · scope & non-goals · the right-sized model/effort · and it keeps the rewrite
lean.

## Before → after
**Before:** "write me something about our new feature for the blog"

**After:** "Write a 600-word blog post announcing **<feature>** for technical users new to
**<domain>**. Lead with the problem it solves, show one before → after, end with one call to
action. Name the feature in the first line; include one real usage example. Concrete, no
fluff."

## Why trust the rules
Every rule nail-it applies came out of a **measured** study on a real production LLM agent —
tightening the spec beat upgrading the model, every time. The receipts and the full method
(the advanced [`tokenomics`](../tokenomics/) skill) live in this repo.

MIT licensed.
