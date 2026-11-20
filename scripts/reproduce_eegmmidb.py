"""Posterior-to-anterior alpha dPTE at rest, raw vs surrogate-corrected.

Data: PhysioNet EEG Motor Movement/Imagery Database (EEGMMIDB), run R02 (eyes-closed
baseline, 60 s, 64 channels, 160 Hz). Download the EDF files from
https://physionet.org/content/eegmmidb/1.0.0/ (or with mne.datasets.eegbci.load_data).
No data are included in this repository.

For each subject: band-pass 8-12 Hz, Hilbert phase, dPTE between every posterior
(O, PO, Iz) and anterior (Fp, AF, F; not FC/FT) channel, then the mean posterior->anterior
value. Two nulls, both of which keep each channel's own signal and destroy only the
timing between regions:
  shift - circularly shift the anterior block in time (keeps everything within each channel)
  aaft  - amplitude-adjusted Fourier surrogates per channel (keeps spectrum and amplitude
          distribution; also destroys within-channel nonlinearity such as alpha bursts)
Corrected dPTE = observed - mean(surrogates) + 0.5.

Usage:
  python scripts/reproduce_eegmmidb.py <edf_dir> [--subjects 1-30] [--exclude 23]
         [--refs avg csd] [--methods shift aaft] [--nsurr 200] [--out results/eegmmidb_R02.csv]
"""
import argparse, glob, os, sys
import numpy as np, pandas as pd, mne
from mne.datasets import eegbci
from scipy.signal import hilbert
from scipy.stats import wilcoxon
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from dpte import dpte, delay, aaft_multi
mne.set_log_level('ERROR')

def subject_list(spec, exclude):
    a, _, b = spec.partition('-')
    subs = range(int(a), int(b or a) + 1)
    return [s for s in subs if s not in exclude]

def analyze(fn, ref, method, nsurr):
    sub = int(os.path.basename(fn)[1:4])
    rng = np.random.default_rng(sub)                  # seeded by subject number
    raw = mne.io.read_raw_edf(fn, preload=True)
    eegbci.standardize(raw); raw.set_montage('standard_1005'); raw.filter(1., 40.)
    r = raw.copy().set_eeg_reference('average')
    if ref == 'csd':
        r = mne.preprocessing.compute_current_source_density(r)
    ch = r.ch_names
    post = [i for i, c in enumerate(ch) if c.startswith(('O', 'PO', 'Iz'))]
    ant = [i for i, c in enumerate(ch) if c.startswith(('Fp', 'AF', 'F')) and not c.startswith(('FC', 'FT'))]
    npo = len(post)
    X = r.get_data()[post + ant]

    def phases(x):
        a = mne.io.RawArray(x, mne.create_info(len(x), r.info['sfreq'], 'eeg')).filter(8., 12.).get_data()
        return np.angle(hilbert(a[:, 160:-160], axis=1))  # drop 1 s edges

    ph = phases(X); d = delay(ph)
    obs = dpte(ph, d=d)[0]
    if method == 'aaft':
        S = np.stack([dpte(phases(aaft_multi(X, rng)), d=d)[0] for _ in range(nsurr)], -1)
    else:
        def shifted():
            p = ph.copy(); k = rng.integers(800, p.shape[1] - 800)
            p[npo:] = np.roll(p[npo:], k, axis=1); return p
        S = np.stack([dpte(shifted(), d=d)[0] for _ in range(nsurr)], -1)
    pa_obs = obs[:npo, npo:].mean()
    pa_null = S[:npo, npo:, :].mean(axis=(0, 1))
    return dict(sub=f'S{sub:03d}', ref=ref, method=method, nsurr=nsurr, delay=d, n_post=npo, n_ant=len(ant),
                PA_obs=pa_obs, PA_null_mean=pa_null.mean(), PA_null_p=(pa_null >= pa_obs).mean(),
                PA_corrected=pa_obs - pa_null.mean() + 0.5)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('edf_dir'); p.add_argument('--subjects', default='1-30')
    p.add_argument('--exclude', type=int, nargs='*', default=[23])
    p.add_argument('--refs', nargs='+', default=['avg', 'csd'])
    p.add_argument('--methods', nargs='+', default=['shift', 'aaft'])
    p.add_argument('--nsurr', type=int, default=200)
    p.add_argument('--out', default='results/eegmmidb_R02.csv')
    a = p.parse_args()
    rows = []
    for s in subject_list(a.subjects, a.exclude):
        fn = os.path.join(a.edf_dir, f'S{s:03d}R02.edf')
        if not os.path.exists(fn):
            print(f'missing {fn}, skipped'); continue
        for ref in a.refs:
            for m in a.methods:
                rows.append(analyze(fn, ref, m, a.nsurr)); print(rows[-1], flush=True)
    df = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True); df.to_csv(a.out, index=False)
    print('\nGroup summary (n = %d subjects)' % df['sub'].nunique())
    for (ref, m), g in df.groupby(['ref', 'method']):
        print(f'{ref:>4} {m:>5}: raw {g.PA_obs.mean():.3f} ({(g.PA_obs > 0.5).sum()}/{len(g)} > 0.5, '
              f'Wilcoxon p = {wilcoxon(g.PA_obs - 0.5).pvalue:.1g}) | corrected {g.PA_corrected.mean():.4f} '
              f'(Wilcoxon vs 0.5 p = {wilcoxon(g.PA_corrected - 0.5).pvalue:.2g})')

if __name__ == '__main__':
    main()
