# Case study: does resting alpha flow from back to front?

A worked example of the kind of expert check described in [framework.md](framework.md). It uses public EEG data and the code in this repository. The finding stands on its own as a methods result.

## The question

With eyes closed, scalp EEG is dominated by alpha rhythm (8-12 Hz), strongest over the back of the head. Directed phase transfer entropy (dPTE; Lobier et al., 2014; Hillebrand et al., 2016) is a popular way to estimate the *direction* of interactions between regions: values above 0.5 mean one region leads the other, and 0.5 means no preferred direction. Resting-state MEG work has reported back-to-front (posterior-to-anterior) alpha flow.

Does raw scalp EEG show it?

## Data

PhysioNet EEG Motor Movement/Imagery Database (Schalk et al., 2004; Goldberger et al., 2000), run R02 (eyes-closed baseline, 60 s, 64 channels, 160 Hz), subjects S001-S030 excluding S023 (n = 29). Posterior channels: O1, Oz, O2, PO7, PO3, POz, PO4, PO8, Iz. Anterior channels: all Fp, AF, and F channels (not FC or FT).

## What the raw numbers say

| Reference | Group mean posterior-to-anterior dPTE | Subjects above 0.5 | Wilcoxon vs 0.5 |
|---|---|---|---|
| Average reference | 0.528 | 28 of 29 | p = 5e-8 |
| Surface Laplacian (CSD) | 0.561 | 28 of 29 | p = 8e-9 |

Taken at face value, that is strong, consistent back-to-front flow, in line with the published accounts.

## What happens with a proper null

The question an expert asks first: *what does dPTE return for channels that are not interacting at all?* The answer is not always 0.5.

Two surrogate nulls, both of which keep each channel's own signal and destroy only the timing between regions:

| Reference | Null | Mean of null | Corrected dPTE | Corrected vs 0.5 |
|---|---|---|---|---|
| Average | Time shift | 0.528 | 0.4996 | p = 0.73 |
| CSD | Time shift | 0.561 | 0.5007 | p = 0.97 |
| Average | AAFT | 0.521 | 0.507 | p = 0.001 |
| CSD | AAFT | 0.552 | 0.509 | p = 0.046 |

(Corrected dPTE = observed - mean of 200 surrogates + 0.5. p values are Wilcoxon signed-rank across subjects.)

The time-shift null reproduces essentially the entire raw effect. Shifting the anterior channels in time keeps everything about each channel and breaks only the timing between regions, and the "direction" is still there. So the direction comes from properties of the individual channels, not from interaction between them.

## Why: dPTE reads signal strength as direction

In simulation (`scripts/simulate_bias.py`), two fully independent channels, each an alpha rhythm over a 1/f background, give dPTE near 0.5 when their alpha is similar. When one channel's alpha stands well above its background and the other's falls below it, dPTE drifts to about 0.55 in the direction of the stronger rhythm, with no coupling at all. A strong, narrowband rhythm has a band-limited phase that advances regularly; a weak one's phase is mostly background. dPTE turns that asymmetry into apparent "direction."

With eyes closed, posterior alpha is far stronger than anterior alpha. That is exactly the asymmetry that biases the estimator.

The same simulation confirms the estimator ignores zero-lag mixing (one source projected to two sensors with opposite sign gives about 0.50), so the result does not depend on the volume-conduction and reference debate. It holds under both average reference and CSD.

## The second-order point: which null

AAFT surrogates remove 75-85% of the raw effect but leave a small residual (0.507). That residual is not evidence of coupling. AAFT also destroys structure *within* each channel, such as nonlinearity and the bursting nature of alpha, so it can reject for reasons unrelated to interaction between regions. The time-shift null preserves all of that and isolates the hypothesis actually being asked. Choosing the null is part of the analysis, not a detail.

## What this means

- This does not overturn the published source-space MEG work. It shows that **raw scalp dPTE needs a surrogate correction before any directional claim**, and that the correction should use a null that preserves each channel's own properties.
- It matters most where dPTE is used as an outcome. Anything that changes alpha *power* (sedation, many drugs, injury, eye state, arousal) can change raw dPTE with no change in directed interaction.
- A practical check for any directed connectivity metric: run it on surrogates that keep each signal's own properties, and report results relative to that null rather than to the metric's theoretical midpoint.

## AI agents and this check

When I tested current frontier chat models on this question, they proposed testing subject-level dPTE against 0.5. None ran a surrogate on its own, and one model's sanity check used two equal-strength signals, which never triggers the bias. It is a good example of an analysis step that is easy to compute, easy to over-interpret, and exactly where expert judgment still matters.

## Reproduce

```bash
pip install -r requirements.txt
python scripts/simulate_bias.py
python scripts/reproduce_eegmmidb.py /path/to/eegmmidb_edf_files --nsurr 200
```

Per-subject results from the full run (200 surrogates per subject, reference, and null) are in `results/eegmmidb_R02_results.csv`.

## References

- Goldberger AL et al. (2000) PhysioBank, PhysioToolkit, and PhysioNet. *Circulation* 101:e215-e220.
- Hillebrand A et al. (2016) Direction of information flow in large-scale resting-state networks is frequency-dependent. *PNAS* 113:3867-3872.
- Lobier M, Siebenhuhner F, Palva S, Palva JM (2014) Phase transfer entropy: a novel phase-based measure for directed connectivity in networks coupled by oscillatory interactions. *NeuroImage* 85:853-872.
- Schalk G et al. (2004) BCI2000: a general-purpose brain-computer interface (BCI) system. *IEEE Trans Biomed Eng* 51:1034-1043.
- Theiler J et al. (1992) Testing for nonlinearity in time series: the method of surrogate data. *Physica D* 58:77-94.
