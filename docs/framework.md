# Building expert-level evaluation tasks for AI science agents

These are the working rules I use to build tasks that test whether an AI agent can do real analysis on real scientific data. They come from 20+ years of judging whether analyses support their conclusions (as a researcher, journal reviewer, and NSF panelist) and from building and testing tasks on frontier models.

The goal is narrow: a task should separate an agent that *does the analysis an expert would do* from one that produces a plausible answer. Most of the work is in finding the step where those two diverge.

---

## 1. What a good task looks like

A good task has three properties at once:

- **One defensible answer.** An expert reviewer would agree on it, and a grader can check it without judgment calls.
- **A trap only an expert would catch.** The obvious analysis gives the wrong answer, or the right answer for the wrong reason.
- **It requires touching the data.** Prior knowledge, the literature, or a guess cannot get there.

If any one of these is missing, the task measures something else: recall, prompt-following, or luck.

## 2. Anatomy of a task

| Part | What it is | Notes |
|---|---|---|
| Data snapshot | The data exactly as they exist right before the analysis step being tested | Real, public data. Note every quirk you know about. |
| Prompt | The question, posed at the level a scientist would pose it | Do not hint at the trap. Context that sounds harmless can give it away (see section 6). |
| Answer format | A strict, machine-readable structure (for example, JSON with named fields) | Ask for the number, the verdict, *and* the evidence behind the verdict. |
| Grader | A deterministic check of each field | Tolerances justified by the science, not picked to fit. |
| Trap rationale | A plain statement of what an agent is likely to get wrong and why | This is where the expertise shows. If you cannot write it in a paragraph, the task is not ready. |
| Durability evidence | Proof the answer holds across reasonable analysis choices | Rerun under the alternatives an expert might pick. |
| Anti-shortcut evidence | Proof that guessing fails | Check what the literature or a prompt-only model would say. |
| Model runs | Real runs on current models, with notes on how they failed | A task no model fails is not yet a test. |

## 3. Four criteria

1. **Verifiable.** Every field can be checked automatically. Free-text explanations can be graded only for the presence of specific, named elements (for example, "names a surrogate or null comparison").
2. **Durable.** The answer survives defensible changes in preprocessing, parameters, and method. If a reasonable choice flips the answer, the task is testing that choice, and it should say so in the prompt or be dropped.
3. **Anti-shortcut.** An agent that does not touch the data cannot pass. The best case is when prior knowledge points the wrong way, so a literature-based guess fails.
4. **Calibrated.** The task rewards an answer that knows where its uncertainty comes from. Asking for the *supporting statistic* alongside the verdict is the simplest way to do this: a correct verdict reached by the wrong test still fails.

## 4. Where expert traps come from

These are the places I look first, because they are where trained analysts and AI agents most often part ways:

- **What the estimator does under the null.** Many metrics are not centered where people assume. Directed connectivity, for example, can read signal-strength differences as "direction" (see the [dPTE case study](case-study-dpte.md)). The question to ask is: what does this metric return for signals that are *not* related at all?
- **Choice of null.** Different surrogates test different hypotheses. A null that also destroys structure *within* each signal can reject for reasons that have nothing to do with the hypothesis.
- **Data conventions.** Axis orientation and sign conventions, event codes whose meaning changes between runs, data that were already filtered, units, and channel naming.
- **Missing data that is not random.** Participants who could not finish the hardest condition drop out, and a naive mean understates the effect.
- **The literature's default answer.** If a well-known paper reports an effect under different conditions, an agent will often import that answer instead of testing it.
- **Measurement choice.** Two reasonable measures of the same thing can disagree, for reasons an expert can explain (for example, slow drift dominating an amplitude measure but not a velocity measure).

## 5. Graders

- **Exact or multiple choice** for verdicts.
- **Numeric tolerance** for values, with the window set by the spread across defensible analysis choices (reference scheme, binning, filter, surrogate type), not by convenience.
- **Set overlap** for lists of features, channels, or genes.
- **Multi-field consistency**: all fields must pass together, and the evidence field must match the verdict. This catches "right answer, wrong reason."

## 6. Testing tasks on models

Run each task on at least two current models, both prompt-only and with the data, and write down *how* each one fails. The failure modes I see most often:

- **Wrong null.** Testing a metric against its theoretical "no effect" value (for example, 0.5) without checking whether the estimator is biased.
- **Right answer, wrong reason.** A correct verdict that came from low power or a lucky subset, not from the right test. The same method on the full data would give the wrong answer.
- **Prior-driven answers.** Citing a published result as the expected outcome and building the analysis to confirm it.
- **Sanity checks that cannot fail.** Checking the estimator on idealized inputs (equal-strength signals, clean data) that never trigger the bias.
- **Framing leakage.** A sentence of context in the prompt (for example, "you are validating an endpoint") can cue a model to look for problems it would not otherwise check. Keep task framing neutral, or test both versions.

## 7. When to drop a task

Dropping tasks is part of the method. I drop a task when:

- A frontier model, given the data, solves it with sound reasoning. That is a capability the model already has.
- Part of the answer is available without the raw data (for example, a public table of precomputed values).
- The trap only works because of how the prompt is worded.

## 8. Checklist before a task is final

- [ ] Data are public, versioned, and cited; quirks are documented
- [ ] Prompt contains no hint of the trap
- [ ] Answer format asks for value, verdict, and supporting evidence
- [ ] Grader tolerances are justified by the spread across defensible methods
- [ ] Trap rationale fits in one paragraph
- [ ] Answer holds across the reasonable alternatives (durability runs saved)
- [ ] A literature-based guess fails (anti-shortcut check saved)
- [ ] At least two models tested, failures recorded
- [ ] Analysis code that produces the ground truth is saved and reproducible
