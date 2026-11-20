"""Python port of SMILe surrogate logic (J.C. Mizelle, SMILe_Surrogates_AAFT.m, SMILe_Surrogates_Threshold.m)."""
import numpy as np

def randphase(x, rng):
    X = np.fft.rfft(x)
    ph = rng.uniform(0, 2 * np.pi, X.shape); ph[0] = 0
    if x.size % 2 == 0: ph[-1] = 0
    return np.fft.irfft(np.abs(X) * np.exp(1j * (np.angle(X) + ph)), n=x.size)

def aaft(x, rng):
    """Amplitude-adjusted FT surrogate of a 1-D signal (Theiler 1992), as in SMILe_Surrogates_AAFT."""
    n = x.size
    ranks = np.argsort(np.argsort(x))
    g = np.sort(rng.standard_normal(n))[ranks]          # gaussian with x's rank order
    g = randphase(g, rng)
    return np.sort(x)[np.argsort(np.argsort(g))]        # x's values in phase-randomized rank order

def aaft_multi(data, rng):
    """Independent AAFT per channel: keeps each channel's spectrum and amplitude distribution, destroys cross-channel timing."""
    return np.vstack([aaft(ch, rng) for ch in data])

def threshold(adj, surr, siglevel=0.005):
    """Edge-wise surrogate threshold (SMILe_Surrogates_Threshold): drop edge if adj < surrogate in more than round(nsurr*siglevel) surrogates."""
    counts = (adj[..., None] < surr).sum(-1)
    out = adj.copy(); out[counts > round(surr.shape[-1] * siglevel)] = 0
    np.fill_diagonal(out, 0)
    return out
