# Expert evaluation tasks for AI science agents

How I build tasks that test whether an AI agent can do real analysis on real scientific data, with a worked EEG case study and the code behind it.

**J.C. (Chris) Mizelle, PhD.** Neuroscientist (EEG, MRI, sensorimotor control), long-time journal reviewer and NSF panelist. Much of my career has been judging whether an analysis actually supports its conclusion. This repository applies that to AI.

## What's here

| | |
|---|---|
| [docs/framework.md](docs/framework.md) | The method: what makes a good evaluation task, where expert traps come from, how to grade, how to test tasks on models, and when to drop them |
| [docs/case-study-dpte.md](docs/case-study-dpte.md) | A worked example on public EEG data: raw directed connectivity (dPTE) shows strong back-to-front alpha "flow" in 28 of 29 people, and a proper surrogate null removes it |
| `dpte/` | Directed phase transfer entropy estimator and surrogate tools (Python versions of code from my MATLAB [SMILe](https://github.com/jcmizelle/SMILe) toolbox) |
| `scripts/simulate_bias.py` | Shows dPTE reading signal-strength asymmetry as "direction" between independent signals |
| `scripts/reproduce_eegmmidb.py` | Reproduces the case-study result from the PhysioNet EEG Motor Movement/Imagery Database |
| `results/` | Per-subject results from the full run, and the simulation output |

## The short version

An evaluation task is only useful if the obvious analysis fails and the expert analysis succeeds. In the case study, the obvious analysis tests dPTE against 0.5 and finds strong directed flow (p = 5e-8). The expert analysis first asks what dPTE does with channels that are not interacting at all, runs a surrogate null that keeps each channel's own signal, and finds nothing left (corrected 0.4996, p = 0.73). Current frontier models I tested took the first path.

## Quick start

```bash
pip install -r requirements.txt
python scripts/simulate_bias.py                       # about a minute
python scripts/reproduce_eegmmidb.py /path/to/edf     # run R02 EDF files, S001-S030
```

Data: [PhysioNet EEGMMIDB](https://physionet.org/content/eegmmidb/1.0.0/) (Schalk et al., 2004). No data are stored in this repository; download the EDF files from PhysioNet or with `mne.datasets.eegbci.load_data`.

## Related

- [SMILe](https://github.com/jcmizelle/SMILe) - MATLAB EEG toolbox (connectivity, surrogates, permutation statistics)
- [fMRI-Pipeline](https://github.com/jcmizelle/fMRI-Pipeline) - Bash/FSL/FreeSurfer and SPM pipelines

## License

GPL-3.0. See LICENSE.
