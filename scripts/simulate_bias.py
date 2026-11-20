"""Does dPTE report "direction" between signals that are not coupled at all?

Each simulated channel = an alpha rhythm (a resonant 10 Hz oscillator, like a real alpha
peak) plus 1/f background, as in scalp EEG. The two channels are fully independent.
When one channel carries a stronger alpha rhythm over the background, its band-limited
phase advances more regularly, and dPTE drifts away from 0.5 even though neither signal
drives the other. A final check mixes one source into two sensors with zero lag (volume
conduction) to confirm the estimator itself ignores instantaneous mixing.

Usage: python scripts/simulate_bias.py [--reps 50]
"""
import argparse, os, sys
import numpy as np
from scipy.signal import butter, filtfilt, hilbert, lfilter
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from dpte import dpte

FS, DUR = 160, 60  # match EEGMMIDB baseline runs: 160 Hz, 60 s
N = FS * DUR

def unit(x):
    return x / x.std()

def alpha_rhythm(rng, f0=10.0, r=0.99):
    """Resonant AR(2) oscillator driven by white noise: a spectral peak at f0."""
    w = 2 * np.pi * f0 / FS
    return unit(lfilter([1.0], [1.0, -2 * r * np.cos(w), r * r], rng.standard_normal(N)))

def background(rng):
    """1/f ("pink") background activity."""
    X = np.fft.rfft(rng.standard_normal(N))
    f = np.fft.rfftfreq(N, 1 / FS); f[0] = 1.0
    return unit(np.fft.irfft(X / np.sqrt(f), N))

def band_phase(x):
    b, a = butter(4, [8 / (FS / 2), 12 / (FS / 2)], btype='band')
    y = filtfilt(b, a, x, axis=-1)[:, FS:-FS]          # drop 1 s edges
    return np.angle(hilbert(y, axis=-1))

def pair_dpte(x, y):
    dp, _, _ = dpte(band_phase(np.vstack([x, y])))
    return dp[0, 1]  # >0.5 means x "leads" y

def main(reps):
    rng = np.random.default_rng(1)
    print('Two INDEPENDENT channels (no coupling): alpha amplitude x, alpha amplitude y, each over unit 1/f background')
    print(f'{"alpha x":>8} {"alpha y":>8} {"mean dPTE x->y":>15} {"SD":>6}')
    for ax, ay in [(1, 1), (2, 1), (5, 1), (5, 0.5), (1, 5)]:
        v = [pair_dpte(ax * alpha_rhythm(rng) + background(rng),
                       ay * alpha_rhythm(rng) + background(rng)) for _ in range(reps)]
        print(f'{ax:>8} {ay:>8} {np.mean(v):>15.3f} {np.std(v):>6.3f}')
    v = []
    for _ in range(reps):
        s = alpha_rhythm(rng)
        v.append(pair_dpte(s + 0.3 * background(rng), -0.8 * s + 0.3 * background(rng)))
    print(f'\nZero-lag antiphase mixing of ONE source into two sensors: mean dPTE {np.mean(v):.3f} (SD {np.std(v):.3f})')

if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--reps', type=int, default=50)
    main(p.parse_args().reps)
