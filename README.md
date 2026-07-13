# Reasoning Lab: Pixitex Prototype

A Streamlit prototype that pairs a student with an AI "Reasoning Lab Coach" (built on Claude) that walks
them through short business case studies, challenges whatever choice they make, and scores the reasoning
quality of their responses in the background.

**Status: academic research prototype / artifact.** This is not a validated educational tool, and it has
not been evaluated for reliability, bias, or safety at scale. It exists to let students interact with a
specific reasoning-coaching approach so the approach itself can be studied — the software is disposable;
the interaction data and the design are the point.

## Intended usage protocol

This prototype is designed for a **pre/post, single-session-each** interaction, not ongoing daily use:

1. **Session 1** — a student interacts with the coach once, cold, before any explicit teaching about the
   underlying reasoning concepts (Ladder of Inference, trade-off analysis, etc.).
2. *(Between sessions, students receive some form of instruction/insight outside the app.)*
3. **Session 2** — the same student interacts with the app again, and the two transcripts/scores are
   compared to look for a change in reasoning behavior.

The app currently has **no built-in way to link a student's Session 1 and Session 2 data**, and no
persistent identity or storage — see Limitations below. Matching sessions to students and to each other is
presently a manual, out-of-band process.

## Assumptions this prototype makes

- **The hidden "auditor" LLM call is a valid proxy for reasoning quality.** A single Claude call, given
  only the student's latest message (no conversation context), returns a 0.0–1.0 score and a mental-health
  flag. This is a stand-in for a validated rubric or human rater, not one.
- **Concealing the "Devil's Advocate" framing improves learning.** The system prompt deliberately withholds
  the name of the technique from the student, on the theory that naming it would let students intellectualize
  past the challenge instead of engaging with it. This is a pedagogical hypothesis, not something this
  prototype has tested.
- **The five-step protocol (present → analyze → choose → pivot → trade-off question) can be tracked by the
  model re-reading chat history each turn.** There is no explicit state machine — Claude infers where it is
  in the sequence and which case study is active from context alone.
- **A turn-by-turn Bayesian update is a meaningful "maturity" signal.** `alpha`/`beta` are updated once per
  turn from the auditor's score, and reported as `alpha / (alpha + beta)`. This produces a number that moves
  in a sensible direction, but it has not been validated against any independent measure of reasoning skill.
- **English-language, text-only interaction.** No accommodation for other languages or non-text input.

## Known limitations

- **No persistent, authenticated storage.** Session state (chat history, maturity score, flagged concerns)
  lives only in Streamlit's in-memory session state and is lost when the browser tab closes or the app
  restarts. The `flagged_concerns.log` file used for teacher review is written to the app's local disk,
  which is **ephemeral on Streamlit Community Cloud** — it can be wiped on redeploy, sleep, or restart, and
  is shared across all users of that deployment (no per-student separation). A persistent backend (planned:
  a database with an immutable/append-only record) is intended to replace this.
- **No student identity.** There's no login, so nothing currently links a Session 1 transcript to the same
  student's Session 2 transcript.
- **The reasoning-quality score and mental-health flag are both produced by one low-effort, context-free
  LLM call.** This is a noisy signal for scoring, and a fragile one for safety-relevant flagging — false
  negatives on genuine distress are possible. The flag should be treated as "worth a teacher's attention,"
  never as a reliable detector on its own. It does not replace human oversight of the actual transcripts.
- **Only three case studies exist**, hardcoded into the system prompt. There's no defined behavior for what
  happens once all three are exhausted in one session, or for generating new ones.
- **Guardrails (jailbreak resistance, in-character enforcement, crisis protocol) have not been adversarially
  tested.** They're implemented as system-prompt instructions and have not been red-teamed.
- **Conversation history grows unbounded within a session** — every turn resends the full transcript to the
  model, so cost and latency increase over a long session, with no case-completion or session-end logic to
  cap it.
- **Model behavior can vary run to run** and may drift if the underlying Claude model is updated or swapped.

## Architecture (current)

- `app.py` — Streamlit UI + all logic (system prompt, Claude API calls, Bayesian scoring, flagging).
- `requirements.txt` — `streamlit`, `anthropic`.
- Secrets (`ANTHROPIC_API_KEY`) are supplied via Streamlit Cloud's Secrets manager, not committed to the repo.
